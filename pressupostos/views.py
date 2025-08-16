from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods, require_POST
from django.db import transaction
from django.utils.timezone import now
from django.urls import reverse
from django.template.loader import get_template
from django.core.files import File
from weasyprint import HTML
import tempfile

from .models import Pressupost, PressupostLinia, PressupostPDFVersion
from .forms import (
    PressupostForm,
    PressupostLiniaFormSetCreate,
    PressupostLiniaFormSetEdit
)
from projectes.models import Projecte
from maestros.models import Tasca, Recurso, Desplacament, Treball, Hores

# Helper function para verificar si es admin
def is_admin(user):
    return user.is_authenticated and user.is_superuser


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

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as output:
        HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(output.name)
        output.seek(0)

        nova_pdf = PressupostPDFVersion(
            pressupost=pressupost,
            version=nova_version,
            generat_per=request.user,
            html=html_string  # 👈 Guardamos el HTML generado
        )
        nova_pdf.arxiu.save(f"pressupost_{pressupost.pk}_v{nova_version}.pdf", File(output))

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
    pressupostos = Pressupost.objects.all()
    return render(request, 'pressupostos/list.html', {'pressupostos': pressupostos})


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


def get_projectes_by_client(request, client_id):
    projectes = Projecte.objects.filter(client_id=client_id, tancat=False)
    data = [{'id': p.id, 'nom': p.nom} for p in projectes]
    return JsonResponse(data, safe=False)


def get_tasques_by_treball(request, treball_id):
    try:
        treball = Treball.objects.get(pk=treball_id)
        tasques = treball.tasques.all()
        data = [{'id': t.id, 'tasca': t.tasca} for t in tasques]
        return JsonResponse({'tasques': data})
    except Treball.DoesNotExist:
        return JsonResponse({'error': 'Treball no trobat'}, status=404)


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
def eliminar_pressupost_ajax(request, pk):
    try:
        pressupost = Pressupost.objects.get(pk=pk)
        pressupost.delete()
        return JsonResponse({"success": True})
    except Pressupost.DoesNotExist:
        return JsonResponse({"success": False, "error": "Pressupost no trobat."}, status=404)
