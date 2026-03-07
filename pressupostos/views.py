from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods, require_POST
from django.db import transaction
from django.db.models import Q, ProtectedError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from django.urls import reverse
from django.template.loader import get_template
from django.core.files import File
from django.core.files.base import ContentFile
from weasyprint import HTML
from datetime import datetime
from decimal import Decimal
import csv
import tempfile

from .models import Pressupost, PressupostLinia, PressupostPDFVersion
from .forms import (
    PressupostForm,
    PressupostLiniaFormSetCreate,
    PressupostLiniaFormSetEdit
)
from projectes.models import Projecte
from maestros.models import Tasca, Recurso, Desplacament, Treball, Hores
from carregahores.models import CarregaHores

# Helper function para verificar si es admin
def is_admin(user):
    return user.is_authenticated and user.is_superuser


def can_view_hores_report(user):
    return user.is_authenticated and (
        user.is_superuser or user.has_perm("pressupostos.view_hores_report")
    )


def _parse_iso_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _get_hores_report_context(request):
    client_id = request.GET.get("client_id", "").strip()
    projecte_id = request.GET.get("projecte_id", "").strip()
    tasca_id = request.GET.get("tasca_id", "").strip()
    recurs_id = request.GET.get("recurs_id", "").strip()
    data_inici = _parse_iso_date(request.GET.get("data_inici", "").strip())
    data_fi = _parse_iso_date(request.GET.get("data_fi", "").strip())

    linies_qs = PressupostLinia.objects.select_related(
        "pressupost__client",
        "pressupost__projecte",
        "tasca",
        "recurs",
    )

    if client_id:
        linies_qs = linies_qs.filter(pressupost__client_id=client_id)
    if projecte_id:
        linies_qs = linies_qs.filter(pressupost__projecte_id=projecte_id)
    if tasca_id:
        linies_qs = linies_qs.filter(tasca_id=tasca_id)
    if recurs_id:
        linies_qs = linies_qs.filter(recurs_id=recurs_id)
    if data_inici:
        linies_qs = linies_qs.filter(pressupost__data__gte=data_inici)
    if data_fi:
        linies_qs = linies_qs.filter(pressupost__data__lte=data_fi)

    carregues_qs = CarregaHores.objects.select_related(
        "linia__pressupost__client",
        "linia__pressupost__projecte",
        "linia__tasca",
        "linia__recurs",
    )
    if client_id:
        carregues_qs = carregues_qs.filter(linia__pressupost__client_id=client_id)
    if projecte_id:
        carregues_qs = carregues_qs.filter(linia__pressupost__projecte_id=projecte_id)
    if tasca_id:
        carregues_qs = carregues_qs.filter(linia__tasca_id=tasca_id)
    if recurs_id:
        carregues_qs = carregues_qs.filter(linia__recurs_id=recurs_id)
    if data_inici:
        carregues_qs = carregues_qs.filter(data__gte=data_inici)
    if data_fi:
        carregues_qs = carregues_qs.filter(data__lte=data_fi)

    grouped = {}

    for linia in linies_qs:
        key = (linia.pressupost.projecte_id, linia.tasca_id)
        if key not in grouped:
            grouped[key] = {
                "projecte_nom": str(linia.pressupost.projecte),
                "tasca_nom": str(linia.tasca),
                "hores_previstes": Decimal("0"),
                "hores_reals": Decimal("0"),
            }
        grouped[key]["hores_previstes"] += linia.hores_totals or Decimal("0")

    for carrega in carregues_qs:
        projecte = carrega.linia.pressupost.projecte
        tasca = carrega.linia.tasca
        key = (projecte.id, tasca.id)
        if key not in grouped:
            grouped[key] = {
                "projecte_nom": str(projecte),
                "tasca_nom": str(tasca),
                "hores_previstes": Decimal("0"),
                "hores_reals": Decimal("0"),
            }
        grouped[key]["hores_reals"] += carrega.hores or Decimal("0")

    rows = []
    for row in grouped.values():
        previstes = row["hores_previstes"]
        reals = row["hores_reals"]
        desviacio = reals - previstes
        row["desviacio"] = desviacio
        row["consum_percent"] = (reals / previstes * Decimal("100")) if previstes > 0 else None
        rows.append(row)

    rows.sort(key=lambda r: (r["projecte_nom"].lower(), r["tasca_nom"].lower()))

    totals_previstes = sum((r["hores_previstes"] for r in rows), Decimal("0"))
    totals_reals = sum((r["hores_reals"] for r in rows), Decimal("0"))
    totals_desviacio = totals_reals - totals_previstes
    totals_consum_percent = (
        (totals_reals / totals_previstes * Decimal("100")) if totals_previstes > 0 else None
    )

    return {
        "rows": rows,
        "totals_previstes": totals_previstes,
        "totals_reals": totals_reals,
        "totals_desviacio": totals_desviacio,
        "totals_consum_percent": totals_consum_percent,
        "filters": {
            "client_id": client_id,
            "projecte_id": projecte_id,
            "tasca_id": tasca_id,
            "recurs_id": recurs_id,
            "data_inici": data_inici.isoformat() if data_inici else "",
            "data_fi": data_fi.isoformat() if data_fi else "",
        },
    }


# --- GENERAR PDF I GUARDAR ---
@user_passes_test(is_admin, login_url='/admin/login/')
def generar_pdf_y_guardar(request, pressupost_id):
    pressupost = get_object_or_404(Pressupost, pk=pressupost_id)
    linies = pressupost.linies.all()
    total = sum([l.total or 0 for l in linies])

    ultima_version = PressupostPDFVersion.objects.filter(pressupost=pressupost).first()
    nova_version = ultima_version.version + 1 if ultima_version else 1

    template = get_template("pressupostos/pdf.html")
    html_string = template.render({
        "pressupost": pressupost,
        "linies": linies,
        "total_pressupost": total,
        "logo_url": request.build_absolute_uri("/static/logo_ecodisseny_positiu.png"),
        "now": now(),
        "generat_per": request.user.get_full_name() or request.user.username
    })

    try:
        # Crear el PDF en memoria primero
        pdf_content = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
        
        # Crear el objeto PressupostPDFVersion
        nova_pdf = PressupostPDFVersion(
            pressupost=pressupost,
            version=nova_version,
            generat_per=request.user,
            html=html_string
        )
        
        # Guardar el PDF
        pdf_file = ContentFile(pdf_content)
        nova_pdf.arxiu.save(
            f"pressupost_{pressupost.pk}_v{nova_version}.pdf", 
            pdf_file,
            save=True
        )
        
        messages.success(request, f'PDF versió {nova_version} generat correctament.')
        
    except Exception as e:
        messages.error(request, f'Error al generar el PDF: {str(e)}')

    return HttpResponseRedirect(reverse("pressupostos:detall", args=[pressupost.pk]))


# --- PDF VIEW ---
@user_passes_test(is_admin, login_url='/admin/login/')
def veure_pdf_pressupost(request, id):
    pressupost = get_object_or_404(Pressupost, pk=id)
    linies = pressupost.linies.all()
    total = sum([l.total or 0 for l in linies])

    template = get_template("pressupostos/pdf.html")
    html_string = template.render({
        "pressupost": pressupost,
        "linies": linies,
        "total_pressupost": total,
        "logo_url": request.build_absolute_uri("/static/logo_ecodisseny_positiu.png"),
        "now": now(),
        "generat_per": request.user.get_full_name() or request.user.username
    })

    response = HttpResponse(content_type="application/pdf")
    filename = f'pressupost_{pressupost.pk}.pdf'
    response["Content-Disposition"] = f'inline; filename="{filename}"'

    with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as output:
        HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(output.name)
        output.seek(0)
        response.write(output.read())

    return response


# --- DETALL ---
@user_passes_test(is_admin, login_url='/admin/login/')
def detail_view(request, pk):
    pressupost = get_object_or_404(Pressupost, pk=pk)
    versions = pressupost.pdf_versions.order_by('-version')
    return render(request, 'pressupostos/detail.html', {
        'pressupost': pressupost,
        'versions': versions,
    })


# --- LLISTAT ---
@user_passes_test(is_admin, login_url='/admin/login/')
def list_pressuposts(request):
    # Inicializar variables de contexto
    context = {
        'pressupostos': [],
        'q': '',
        'tancat': '',
        'data_inici': None,
        'data_fi': None
    }
    
    try:
        # Obtener los filtros
        q = request.GET.get('q', '').strip()
        tancat = request.GET.get('tancat', '')
        
        # Query base con todas las relaciones necesarias
        pressupostos = Pressupost.objects.select_related('client', 'projecte').all()
        
        # Aplicar filtros si existen
        if q:
            pressupostos = pressupostos.filter(
                Q(nom__icontains=q) |
                Q(client__nom_client__icontains=q) |
                Q(projecte__nom__icontains=q)
            )
            
        if tancat in ['true', 'false']:
            pressupostos = pressupostos.filter(tancat=(tancat == 'true'))
            
        # Actualizar contexto
        context.update({
            'pressupostos': pressupostos.order_by('-data'),  # Ordenar por fecha descendente
            'q': q,
            'tancat': tancat
        })
        
    except Exception as e:
        messages.error(request, f'Error al cargar els pressupostos: {str(e)}')
    
    return render(request, 'pressupostos/list.html', context)


@user_passes_test(can_view_hores_report, login_url='/admin/login/')
def informe_hores(request):
    data = _get_hores_report_context(request)
    context = {
        **data,
        "clients": Pressupost.objects.select_related("client").values_list("client_id", "client__nom_client").distinct().order_by("client__nom_client"),
        "projectes": Projecte.objects.values_list("id", "nom").order_by("nom"),
        "tasques": Tasca.objects.values_list("id", "tasca").order_by("tasca"),
        "recursos": Recurso.objects.values_list("id", "nom").order_by("nom"),
        "query_string": request.GET.urlencode(),
    }
    return render(request, "pressupostos/informe_hores.html", context)


@user_passes_test(can_view_hores_report, login_url='/admin/login/')
def informe_hores_csv(request):
    data = _get_hores_report_context(request)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="informe_hores_pressupostos.csv"'

    writer = csv.writer(response)
    writer.writerow(["Projecte", "Tasca", "Hores Previstes", "Hores Reals", "Desviacio", "% Consum"])
    for row in data["rows"]:
        writer.writerow([
            row["projecte_nom"],
            row["tasca_nom"],
            f'{row["hores_previstes"]:.2f}',
            f'{row["hores_reals"]:.2f}',
            f'{row["desviacio"]:.2f}',
            (f'{row["consum_percent"]:.2f}' if row["consum_percent"] is not None else ""),
        ])
    writer.writerow([])
    writer.writerow([
        "TOTAL",
        "",
        f'{data["totals_previstes"]:.2f}',
        f'{data["totals_reals"]:.2f}',
        f'{data["totals_desviacio"]:.2f}',
        (f'{data["totals_consum_percent"]:.2f}' if data["totals_consum_percent"] is not None else ""),
    ])
    return response


@user_passes_test(is_admin, login_url='/admin/login/')
@require_POST
def delete_version_ajax(request, version_id):
    try:
        version = PressupostPDFVersion.objects.get(id=version_id)
        version.arxiu.delete(save=False)  # Borra el arxiu físic
        version.delete()
        return JsonResponse({"success": True})
    except PressupostPDFVersion.DoesNotExist:
        return JsonResponse({"success": False, "error": "Versió no trobada"})


# --- FORMULARI ---
@user_passes_test(is_admin, login_url='/admin/login/')
def form_pressupost(request, id=None):
    pressupost = get_object_or_404(Pressupost, pk=id) if id else None

    if request.method == 'POST':
        form = PressupostForm(request.POST, instance=pressupost)
        formset_class = PressupostLiniaFormSetEdit if pressupost else PressupostLiniaFormSetCreate
        formset = formset_class(request.POST, instance=pressupost or Pressupost())

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    pressupost = form.save(commit=False)
                    pressupost.save()
                    formset.instance = pressupost
                    formset.save()
                messages.success(request, 'Pressupost guardat correctament.')
                return redirect('pressupostos:list')
            except Exception as e:
                messages.error(request, f'Error al guardar: {str(e)}')
        else:
            messages.error(request, 'Formulari invàlid.')
    else:
        form = PressupostForm(instance=pressupost)
        formset = (PressupostLiniaFormSetEdit if pressupost else PressupostLiniaFormSetCreate)(instance=pressupost or Pressupost())

    return render(request, 'pressupostos/form.html', {
        'form': form,
        'pressupost': pressupost,
        'formset': formset,
        'hores_list': Hores.objects.all(),
    })


# --- ELIMINACIÓ ---
@user_passes_test(is_admin, login_url='/admin/login/')
@require_http_methods(["POST"])
def delete_pressupost(request, id):
    pressupost = get_object_or_404(Pressupost, pk=id)
    pressupost.delete()
    messages.success(request, 'Pressupost eliminat correctament.')
    return redirect('pressupostos:list')


# --- AJAX ---
@user_passes_test(is_admin, login_url='/admin/login/')
def get_increment_hores(request):
    id_parroquia = request.GET.get("id_parroquia")
    id_ubicacio = request.GET.get("id_ubicacio")
    id_tasca = request.GET.get("id_tasca")

    if not (id_parroquia and id_ubicacio and id_tasca):
        return JsonResponse({"error": "Falten paràmetres"}, status=400)

    try:
        desplacament = Desplacament.objects.filter(
            parroquia_id=id_parroquia,
            ubicacio_id=id_ubicacio,
            tasca_id=id_tasca
        ).first()
        increment = desplacament.increment_hores if desplacament else 0
        return JsonResponse({"increment_hores": float(increment)})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@user_passes_test(is_admin, login_url='/admin/login/')
def get_projectes_by_client(request, client_id):
    projectes = Projecte.objects.filter(client_id=client_id, tancat=False)
    data = [{'id': p.id, 'nom': p.nom} for p in projectes]
    return JsonResponse(data, safe=False)


@user_passes_test(is_admin, login_url='/admin/login/')
def get_tasques_by_treball(request, treball_id):
    try:
        treball = Treball.objects.get(pk=treball_id)
        tasques = treball.tasques.all()
        data = [{'id': t.id, 'tasca': t.tasca} for t in tasques]
        return JsonResponse({'tasques': data})
    except Treball.DoesNotExist:
        return JsonResponse({'error': 'Treball no trobat'}, status=404)


@user_passes_test(is_admin, login_url='/admin/login/')
def get_recurso_by_id(request, recurs_id):
    recurs = Recurso.objects.filter(pk=recurs_id).exclude(pk=1).first()
    if recurs:
        return JsonResponse({
            "PreuTancat": recurs.preu_tancat,
            "PreuHora": recurs.preu_hora if not recurs.preu_tancat else None
        })
    return JsonResponse({"error": "Recurs no trobat"}, status=404)


@require_POST
@user_passes_test(is_admin, login_url='/admin/login/')
@require_POST
def eliminar_pressupost_ajax(request, pk):
    try:
        pressupost = Pressupost.objects.get(pk=pk)
        nom_pressupost = pressupost.nom or f"Pressupost #{pk}"
        
        # Verificar si tiene horas cargadas
        horas_count = CarregaHores.objects.filter(pressupost=pressupost).count()
        
        if horas_count > 0:
            return JsonResponse({
                "success": False,
                "error": f"No es pot eliminar aquest pressupost perquè té {horas_count} registre(s) d'hores carregades associat(s). Elimina primer les hores carregades."
            }, status=400)
        
        pressupost.delete()
        return JsonResponse({
            "success": True, 
            "message": f"S'ha eliminat el pressupost '{nom_pressupost}' correctament."
        })
    except Pressupost.DoesNotExist:
        return JsonResponse({
            "success": False, 
            "error": "Pressupost no trobat."
        }, status=404)
    except ProtectedError as e:
        # Analizar qué está causando la protección
        protected_objects = e.protected_objects
        error_msg = "No es pot eliminar aquest pressupost per les següents relacions:\n"
        
        for obj in list(protected_objects)[:5]:  # Mostrar máximo 5
            error_msg += f"- {obj._meta.verbose_name}: {str(obj)}\n"
        
        if len(protected_objects) > 5:
            error_msg += f"... i {len(protected_objects) - 5} més"
            
        return JsonResponse({
            "success": False,
            "error": error_msg
        }, status=400)
    except Exception as e:
        import traceback
        return JsonResponse({
            "success": False,
            "error": f"Error inesperat: {str(e)}",
            "traceback": traceback.format_exc()
        }, status=500)
