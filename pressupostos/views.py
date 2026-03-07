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


def can_view_rentabilitat_report(user):
    return user.is_authenticated and (
        user.is_superuser or user.has_perm("pressupostos.view_rentabilitat_report")
    )


def can_view_productivitat_report(user):
    return user.is_authenticated and (
        user.is_superuser or user.has_perm("pressupostos.view_productivitat_report")
    )


def can_view_executiu_report(user):
    return user.is_authenticated and (
        user.is_superuser or user.has_perm("pressupostos.view_executiu_report")
    )


def _parse_iso_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _parse_year_month(value):
    if not value:
        return None
    try:
        dt = datetime.strptime(value, "%Y-%m")
        return dt.year, dt.month
    except ValueError:
        return None


def _month_range(year, month):
    start = datetime(year, month, 1).date()
    if month == 12:
        end = datetime(year + 1, 1, 1).date()
    else:
        end = datetime(year, month + 1, 1).date()
    return start, end


def _get_hores_report_context(request):
    client_id = request.GET.get("client_id", "").strip()
    projecte_id = request.GET.get("projecte_id", "").strip()
    treball_id = request.GET.get("treball_id", "").strip()
    tasca_id = request.GET.get("tasca_id", "").strip()
    recurs_id = request.GET.get("recurs_id", "").strip()
    data_inici = _parse_iso_date(request.GET.get("data_inici", "").strip())
    data_fi = _parse_iso_date(request.GET.get("data_fi", "").strip())

    linies_qs = PressupostLinia.objects.select_related(
        "pressupost__client",
        "pressupost__projecte",
        "treball",
        "tasca",
        "recurs",
    )

    if client_id:
        linies_qs = linies_qs.filter(pressupost__client_id=client_id)
    if projecte_id:
        linies_qs = linies_qs.filter(pressupost__projecte_id=projecte_id)
    if treball_id:
        linies_qs = linies_qs.filter(treball_id=treball_id)
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
        "linia__treball",
        "linia__tasca",
        "linia__recurs",
    )
    if client_id:
        carregues_qs = carregues_qs.filter(linia__pressupost__client_id=client_id)
    if projecte_id:
        carregues_qs = carregues_qs.filter(linia__pressupost__projecte_id=projecte_id)
    if treball_id:
        carregues_qs = carregues_qs.filter(linia__treball_id=treball_id)
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
        key = (linia.pressupost.projecte_id, linia.treball_id, linia.tasca_id)
        if key not in grouped:
            grouped[key] = {
                "projecte_nom": str(linia.pressupost.projecte),
                "treball_nom": str(linia.treball),
                "tasca_nom": str(linia.tasca),
                "hores_previstes": Decimal("0"),
                "hores_reals": Decimal("0"),
            }
        grouped[key]["hores_previstes"] += linia.hores_totals or Decimal("0")

    for carrega in carregues_qs:
        projecte = carrega.linia.pressupost.projecte
        treball = carrega.linia.treball
        tasca = carrega.linia.tasca
        key = (projecte.id, treball.id, tasca.id)
        if key not in grouped:
            grouped[key] = {
                "projecte_nom": str(projecte),
                "treball_nom": str(treball),
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

    rows.sort(key=lambda r: (r["projecte_nom"].lower(), r["treball_nom"].lower(), r["tasca_nom"].lower()))

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
            "treball_id": treball_id,
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
        "treballs": Treball.objects.values_list("id", "descripcio").order_by("descripcio"),
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
    writer.writerow(["Projecte", "Treball", "Tasca", "Hores Previstes", "Hores Reals", "Desviacio", "% Consum"])
    for row in data["rows"]:
        writer.writerow([
            row["projecte_nom"],
            row["treball_nom"],
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
        "",
        f'{data["totals_previstes"]:.2f}',
        f'{data["totals_reals"]:.2f}',
        f'{data["totals_desviacio"]:.2f}',
        (f'{data["totals_consum_percent"]:.2f}' if data["totals_consum_percent"] is not None else ""),
    ])
    return response


def _get_rentabilitat_context(request):
    client_id = request.GET.get("client_id", "").strip()
    projecte_id = request.GET.get("projecte_id", "").strip()
    data_inici = _parse_iso_date(request.GET.get("data_inici", "").strip())
    data_fi = _parse_iso_date(request.GET.get("data_fi", "").strip())

    try:
        umbral_amber = Decimal(request.GET.get("umbral_amber", "10").strip() or "10")
    except Exception:
        umbral_amber = Decimal("10")
    try:
        umbral_red = Decimal(request.GET.get("umbral_red", "20").strip() or "20")
    except Exception:
        umbral_red = Decimal("20")
    if umbral_red < umbral_amber:
        umbral_red = umbral_amber

    pressupostos_qs = Pressupost.objects.select_related("client", "projecte").all()
    if client_id:
        pressupostos_qs = pressupostos_qs.filter(client_id=client_id)
    if projecte_id:
        pressupostos_qs = pressupostos_qs.filter(projecte_id=projecte_id)
    if data_inici:
        pressupostos_qs = pressupostos_qs.filter(data__gte=data_inici)
    if data_fi:
        pressupostos_qs = pressupostos_qs.filter(data__lte=data_fi)

    pressupost_ids = list(pressupostos_qs.values_list("id", flat=True))
    linies_qs = PressupostLinia.objects.select_related("pressupost").filter(pressupost_id__in=pressupost_ids)
    carregues_qs = CarregaHores.objects.select_related("linia", "pressupost").filter(pressupost_id__in=pressupost_ids)
    if data_inici:
        carregues_qs = carregues_qs.filter(data__gte=data_inici)
    if data_fi:
        carregues_qs = carregues_qs.filter(data__lte=data_fi)

    grouped = {}
    for p in pressupostos_qs:
        grouped[p.id] = {
            "pressupost_id": p.id,
            "pressupost_nom": p.nom or f"Pressupost #{p.id}",
            "client_nom": str(p.client),
            "projecte_nom": str(p.projecte),
            "data": p.data,
            "ingres_previst": Decimal("0"),
            "cost_previst": Decimal("0"),
            "cost_real": Decimal("0"),
        }

    for linia in linies_qs:
        row = grouped.get(linia.pressupost_id)
        if not row:
            continue
        row["ingres_previst"] += linia.total or Decimal("0")
        row["cost_previst"] += linia.subtotal or Decimal("0")

    for carrega in carregues_qs:
        row = grouped.get(carrega.pressupost_id)
        if not row:
            continue
        linia = carrega.linia
        cost_hora_real = linia.cost_hores or Decimal("0")
        if linia.aplicar_cost_hores is False:
            cost_hora_real = Decimal("0")
        row["cost_real"] += (carrega.hores or Decimal("0")) * cost_hora_real

    rows = []
    for row in grouped.values():
        ingres_previst = row["ingres_previst"]
        cost_previst = row["cost_previst"]
        cost_real = row["cost_real"]
        marge_previst = ingres_previst - cost_previst
        marge_real = ingres_previst - cost_real
        desviacio_cost = cost_real - cost_previst
        desviacio_percent = (
            (desviacio_cost / cost_previst * Decimal("100")) if cost_previst > 0 else None
        )

        if desviacio_percent is None:
            semafor = "secondary"
            semafor_label = "Sense base"
        elif desviacio_percent >= umbral_red:
            semafor = "danger"
            semafor_label = "Roig"
        elif desviacio_percent >= umbral_amber:
            semafor = "warning"
            semafor_label = "Ambre"
        else:
            semafor = "success"
            semafor_label = "Verd"

        row.update({
            "marge_previst": marge_previst,
            "marge_real": marge_real,
            "desviacio_cost": desviacio_cost,
            "desviacio_percent": desviacio_percent,
            "semafor": semafor,
            "semafor_label": semafor_label,
        })
        rows.append(row)

    rows.sort(key=lambda r: (r["data"], r["pressupost_nom"]))

    total_ingres_previst = sum((r["ingres_previst"] for r in rows), Decimal("0"))
    total_cost_previst = sum((r["cost_previst"] for r in rows), Decimal("0"))
    total_cost_real = sum((r["cost_real"] for r in rows), Decimal("0"))
    total_marge_previst = total_ingres_previst - total_cost_previst
    total_marge_real = total_ingres_previst - total_cost_real
    total_desviacio_cost = total_cost_real - total_cost_previst
    total_desviacio_percent = (
        (total_desviacio_cost / total_cost_previst * Decimal("100")) if total_cost_previst > 0 else None
    )

    return {
        "rows": rows,
        "totals": {
            "ingres_previst": total_ingres_previst,
            "cost_previst": total_cost_previst,
            "cost_real": total_cost_real,
            "marge_previst": total_marge_previst,
            "marge_real": total_marge_real,
            "desviacio_cost": total_desviacio_cost,
            "desviacio_percent": total_desviacio_percent,
        },
        "filters": {
            "client_id": client_id,
            "projecte_id": projecte_id,
            "data_inici": data_inici.isoformat() if data_inici else "",
            "data_fi": data_fi.isoformat() if data_fi else "",
            "umbral_amber": str(umbral_amber),
            "umbral_red": str(umbral_red),
        },
    }


@user_passes_test(can_view_rentabilitat_report, login_url='/admin/login/')
def informe_rentabilitat(request):
    data = _get_rentabilitat_context(request)
    context = {
        **data,
        "clients": Pressupost.objects.select_related("client").values_list("client_id", "client__nom_client").distinct().order_by("client__nom_client"),
        "projectes": Projecte.objects.values_list("id", "nom").order_by("nom"),
        "query_string": request.GET.urlencode(),
    }
    return render(request, "pressupostos/informe_rentabilitat.html", context)


@user_passes_test(can_view_rentabilitat_report, login_url='/admin/login/')
def informe_rentabilitat_csv(request):
    data = _get_rentabilitat_context(request)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="informe_rentabilitat_pressupostos.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "Data",
        "Pressupost",
        "Client",
        "Projecte",
        "Ingres Previst",
        "Cost Previst",
        "Cost Real",
        "Marge Previst",
        "Marge Real",
        "Desviacio Cost",
        "% Desviacio Cost",
        "Semafor",
    ])
    for row in data["rows"]:
        writer.writerow([
            row["data"].isoformat(),
            row["pressupost_nom"],
            row["client_nom"],
            row["projecte_nom"],
            f'{row["ingres_previst"]:.2f}',
            f'{row["cost_previst"]:.2f}',
            f'{row["cost_real"]:.2f}',
            f'{row["marge_previst"]:.2f}',
            f'{row["marge_real"]:.2f}',
            f'{row["desviacio_cost"]:.2f}',
            (f'{row["desviacio_percent"]:.2f}' if row["desviacio_percent"] is not None else ""),
            row["semafor_label"],
        ])
    writer.writerow([])
    writer.writerow([
        "TOTAL",
        "",
        "",
        "",
        f'{data["totals"]["ingres_previst"]:.2f}',
        f'{data["totals"]["cost_previst"]:.2f}',
        f'{data["totals"]["cost_real"]:.2f}',
        f'{data["totals"]["marge_previst"]:.2f}',
        f'{data["totals"]["marge_real"]:.2f}',
        f'{data["totals"]["desviacio_cost"]:.2f}',
        (f'{data["totals"]["desviacio_percent"]:.2f}' if data["totals"]["desviacio_percent"] is not None else ""),
        "",
    ])
    return response


def _get_productivitat_context(request):
    usuari_id = request.GET.get("usuari_id", "").strip()
    recurs_id = request.GET.get("recurs_id", "").strip()
    projecte_id = request.GET.get("projecte_id", "").strip()
    tasca_id = request.GET.get("tasca_id", "").strip()
    data_inici = _parse_iso_date(request.GET.get("data_inici", "").strip())
    data_fi = _parse_iso_date(request.GET.get("data_fi", "").strip())

    qs = CarregaHores.objects.select_related(
        "usuari",
        "linia__recurs",
        "linia__tasca",
        "linia__pressupost__projecte",
    )
    if usuari_id:
        qs = qs.filter(usuari_id=usuari_id)
    if recurs_id:
        qs = qs.filter(linia__recurs_id=recurs_id)
    if projecte_id:
        qs = qs.filter(linia__pressupost__projecte_id=projecte_id)
    if tasca_id:
        qs = qs.filter(linia__tasca_id=tasca_id)
    if data_inici:
        qs = qs.filter(data__gte=data_inici)
    if data_fi:
        qs = qs.filter(data__lte=data_fi)

    grouped = {}
    top_tasca = {}
    total_hores = Decimal("0")
    hores_facturables = Decimal("0")
    hores_no_facturables = Decimal("0")

    for c in qs:
        mes = c.data.strftime("%Y-%m")
        recurs = c.linia.recurs
        tasca = c.linia.tasca
        projecte = c.linia.pressupost.projecte
        key = (mes, recurs.id, projecte.id, tasca.id)
        if key not in grouped:
            grouped[key] = {
                "mes": mes,
                "recurs_nom": str(recurs),
                "projecte_nom": str(projecte),
                "tasca_nom": str(tasca),
                "hores": Decimal("0"),
            }
        hores = c.hores or Decimal("0")
        grouped[key]["hores"] += hores

        top_key = (tasca.id, str(tasca))
        top_tasca[top_key] = top_tasca.get(top_key, Decimal("0")) + hores

        total_hores += hores
        # Proxy de facturable/no facturable según si la línea tiene subtotal previsto > 0.
        if (c.linia.subtotal or Decimal("0")) > 0:
            hores_facturables += hores
        else:
            hores_no_facturables += hores

    detail_rows = list(grouped.values())
    detail_rows.sort(key=lambda r: (r["mes"], r["recurs_nom"].lower(), r["projecte_nom"].lower(), r["tasca_nom"].lower()))

    top_tasques_rows = [
        {"tasca_nom": name, "hores": hores}
        for (_, name), hores in top_tasca.items()
    ]
    top_tasques_rows.sort(key=lambda r: r["hores"], reverse=True)
    top_tasques_rows = top_tasques_rows[:10]

    return {
        "detail_rows": detail_rows,
        "top_tasques_rows": top_tasques_rows,
        "totals": {
            "total_hores": total_hores,
            "hores_facturables": hores_facturables,
            "hores_no_facturables": hores_no_facturables,
        },
        "filters": {
            "usuari_id": usuari_id,
            "recurs_id": recurs_id,
            "projecte_id": projecte_id,
            "tasca_id": tasca_id,
            "data_inici": data_inici.isoformat() if data_inici else "",
            "data_fi": data_fi.isoformat() if data_fi else "",
        },
    }


@user_passes_test(can_view_productivitat_report, login_url='/admin/login/')
def informe_productivitat(request):
    data = _get_productivitat_context(request)
    context = {
        **data,
        "usuaris": CarregaHores.objects.select_related("usuari").values_list("usuari_id", "usuari__username").distinct().order_by("usuari__username"),
        "recursos": Recurso.objects.values_list("id", "nom").order_by("nom"),
        "projectes": Projecte.objects.values_list("id", "nom").order_by("nom"),
        "tasques": Tasca.objects.values_list("id", "tasca").order_by("tasca"),
        "query_string": request.GET.urlencode(),
    }
    return render(request, "pressupostos/informe_productivitat.html", context)


@user_passes_test(can_view_productivitat_report, login_url='/admin/login/')
def informe_productivitat_csv(request):
    data = _get_productivitat_context(request)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="informe_productivitat_recurs.csv"'
    writer = csv.writer(response)
    writer.writerow(["Mes", "Recurs", "Projecte", "Tasca", "Hores"])
    for row in data["detail_rows"]:
        writer.writerow([
            row["mes"],
            row["recurs_nom"],
            row["projecte_nom"],
            row["tasca_nom"],
            f'{row["hores"]:.2f}',
        ])
    writer.writerow([])
    writer.writerow(["TOTAL HORES", f'{data["totals"]["total_hores"]:.2f}'])
    writer.writerow(["HORES FACTURABLES", f'{data["totals"]["hores_facturables"]:.2f}'])
    writer.writerow(["HORES NO FACTURABLES", f'{data["totals"]["hores_no_facturables"]:.2f}'])
    writer.writerow([])
    writer.writerow(["TOP TASQUES", "HORES"])
    for row in data["top_tasques_rows"]:
        writer.writerow([row["tasca_nom"], f'{row["hores"]:.2f}'])
    return response


def _get_executiu_context(request):
    mes_ym = (request.GET.get("mes", "") or "").strip()
    parsed = _parse_year_month(mes_ym)
    if not parsed:
        current = now().date()
        year, month = current.year, current.month
        mes_ym = f"{year:04d}-{month:02d}"
    else:
        year, month = parsed
    month_start, month_end_exclusive = _month_range(year, month)

    client_id = request.GET.get("client_id", "").strip()
    projecte_id = request.GET.get("projecte_id", "").strip()

    pressupostos_qs = Pressupost.objects.select_related("client", "projecte").filter(
        data__gte=month_start,
        data__lt=month_end_exclusive,
    )
    if client_id:
        pressupostos_qs = pressupostos_qs.filter(client_id=client_id)
    if projecte_id:
        pressupostos_qs = pressupostos_qs.filter(projecte_id=projecte_id)

    pressupost_ids = list(pressupostos_qs.values_list("id", flat=True))

    linies_qs = PressupostLinia.objects.select_related("pressupost__projecte").filter(
        pressupost_id__in=pressupost_ids
    )
    carregues_qs = CarregaHores.objects.select_related("linia__pressupost__projecte").filter(
        data__gte=month_start,
        data__lt=month_end_exclusive,
    )
    if client_id:
        carregues_qs = carregues_qs.filter(linia__pressupost__client_id=client_id)
    if projecte_id:
        carregues_qs = carregues_qs.filter(linia__pressupost__projecte_id=projecte_id)

    total_hores_planificades = Decimal("0")
    total_hores_reals = Decimal("0")

    by_project = {}
    for linia in linies_qs:
        pid = linia.pressupost.projecte_id
        if pid not in by_project:
            by_project[pid] = {
                "projecte_nom": str(linia.pressupost.projecte),
                "hores_planificades": Decimal("0"),
                "hores_reals": Decimal("0"),
            }
        hores = linia.hores_totals or Decimal("0")
        by_project[pid]["hores_planificades"] += hores
        total_hores_planificades += hores

    for carrega in carregues_qs:
        pid = carrega.linia.pressupost.projecte_id
        if pid not in by_project:
            by_project[pid] = {
                "projecte_nom": str(carrega.linia.pressupost.projecte),
                "hores_planificades": Decimal("0"),
                "hores_reals": Decimal("0"),
            }
        hores = carrega.hores or Decimal("0")
        by_project[pid]["hores_reals"] += hores
        total_hores_reals += hores

    top_projects = []
    for row in by_project.values():
        desviacio = row["hores_reals"] - row["hores_planificades"]
        row["desviacio"] = desviacio
        row["desviacio_abs"] = abs(desviacio)
        top_projects.append(row)
    top_projects.sort(key=lambda r: (r["desviacio_abs"], r["projecte_nom"].lower()), reverse=True)
    top_projects = top_projects[:10]

    total_pressupostos = pressupostos_qs.count()
    total_tancats = pressupostos_qs.filter(tancat=True).count()
    total_oberts = total_pressupostos - total_tancats
    percent_tancats = (
        (Decimal(total_tancats) / Decimal(total_pressupostos) * Decimal("100"))
        if total_pressupostos > 0 else None
    )
    percent_progres_hores = (
        (total_hores_reals / total_hores_planificades * Decimal("100"))
        if total_hores_planificades > 0 else None
    )

    return {
        "mes": mes_ym,
        "month_label": f"{month:02d}/{year}",
        "totals": {
            "hores_planificades": total_hores_planificades,
            "hores_reals": total_hores_reals,
            "desviacio_hores": total_hores_reals - total_hores_planificades,
            "percent_progres_hores": percent_progres_hores,
        },
        "estat": {
            "total_pressupostos": total_pressupostos,
            "total_tancats": total_tancats,
            "total_oberts": total_oberts,
            "percent_tancats": percent_tancats,
        },
        "top_projects": top_projects,
        "filters": {
            "client_id": client_id,
            "projecte_id": projecte_id,
        },
    }


@user_passes_test(can_view_executiu_report, login_url='/admin/login/')
def informe_executiu_mensual(request):
    data = _get_executiu_context(request)
    context = {
        **data,
        "clients": Pressupost.objects.select_related("client").values_list("client_id", "client__nom_client").distinct().order_by("client__nom_client"),
        "projectes": Projecte.objects.values_list("id", "nom").order_by("nom"),
        "query_string": request.GET.urlencode(),
    }
    return render(request, "pressupostos/informe_executiu_mensual.html", context)


@user_passes_test(can_view_executiu_report, login_url='/admin/login/')
def informe_executiu_mensual_csv(request):
    data = _get_executiu_context(request)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="informe_executiu_mensual.csv"'
    writer = csv.writer(response)
    writer.writerow(["Mes", data["month_label"]])
    writer.writerow(["Hores planificades", f'{data["totals"]["hores_planificades"]:.2f}'])
    writer.writerow(["Hores reals", f'{data["totals"]["hores_reals"]:.2f}'])
    writer.writerow(["Desviacio hores", f'{data["totals"]["desviacio_hores"]:.2f}'])
    writer.writerow(["% progres hores", (f'{data["totals"]["percent_progres_hores"]:.2f}' if data["totals"]["percent_progres_hores"] is not None else "")])
    writer.writerow(["Pressupostos totals", data["estat"]["total_pressupostos"]])
    writer.writerow(["Pressupostos tancats", data["estat"]["total_tancats"]])
    writer.writerow(["Pressupostos oberts", data["estat"]["total_oberts"]])
    writer.writerow(["% tancats", (f'{data["estat"]["percent_tancats"]:.2f}' if data["estat"]["percent_tancats"] is not None else "")])
    writer.writerow([])
    writer.writerow(["Top 10 projectes amb més desviacio", "", "", ""])
    writer.writerow(["Projecte", "Hores planificades", "Hores reals", "Desviacio"])
    for row in data["top_projects"]:
        writer.writerow([
            row["projecte_nom"],
            f'{row["hores_planificades"]:.2f}',
            f'{row["hores_reals"]:.2f}',
            f'{row["desviacio"]:.2f}',
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
