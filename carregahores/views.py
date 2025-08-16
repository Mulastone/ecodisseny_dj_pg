from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .forms import CarregaHoresForm
from .models import CarregaHores
from pressupostos import models as pressupost_models

# Helper function para verificar si es admin
def is_admin(user):
    return user.is_authenticated and user.is_superuser

@login_required
def nova_carrega(request):
    from django.contrib import messages
    
    if request.method == "POST":
        form = CarregaHoresForm(request.POST, user=request.user, initial={"_user": request.user})
        if form.is_valid():
            ch = form.save(commit=False)
            ch.usuari = request.user
            # recurso ya queda seteado en clean() para usuarios normales
            ch.save()
            messages.success(request, f"Càrrega d'hores guardada correctament: {ch.hores} hores el {ch.data.strftime('%d/%m/%Y')}")
            return redirect("carregahores:meves")
    else:
        form = CarregaHoresForm(user=request.user, initial={"_user": request.user})
    return render(request, "carregahores/form.html", {"form": form})


@login_required
def meves_carregues(request):
    from django.db.models import Sum
    
    qs = CarregaHores.objects.all()
    if not request.user.is_superuser:
        qs = qs.filter(usuari=request.user)
    
    # Calcular total de horas
    total_hores = qs.aggregate(total=Sum('hores'))['total'] or 0
    
    context = {
        "items": qs,
        "total_hores": total_hores,
        "total_registres": qs.count()
    }
    return render(request, "carregahores/list.html", context)


# Vista solo para administradores - ver TODAS las cargas
@user_passes_test(is_admin, login_url='/admin/login/')
def totes_carregues_admin(request):
    from django.db.models import Sum
    
    qs = CarregaHores.objects.all().select_related('usuari', 'recurso', 'pressupost', 'treball', 'tasca')
    
    # Calcular totales
    total_hores = qs.aggregate(total=Sum('hores'))['total'] or 0
    
    context = {
        "items": qs,
        "total_hores": total_hores,
        "total_registres": qs.count(),
        "is_admin_view": True
    }
    return render(request, "carregahores/admin_list.html", context)


# Vista solo para administradores - estadísticas
@user_passes_test(is_admin, login_url='/admin/login/')
def estadistiques_admin(request):
    from django.db.models import Sum, Count
    from django.db.models.functions import TruncMonth
    
    # Estadísticas por usuario
    stats_per_user = CarregaHores.objects.values('usuari__username', 'usuari__first_name', 'usuari__last_name').annotate(
        total_hores=Sum('hores'),
        total_registres=Count('id')
    ).order_by('-total_hores')
    
    # Estadísticas por mes
    stats_per_month = CarregaHores.objects.annotate(
        mes=TruncMonth('data')
    ).values('mes').annotate(
        total_hores=Sum('hores'),
        total_registres=Count('id')
    ).order_by('-mes')
    
    # Estadísticas por recurso
    stats_per_recurso = CarregaHores.objects.values('recurso__nom').annotate(
        total_hores=Sum('hores'),
        total_registres=Count('id')
    ).order_by('-total_hores')
    
    context = {
        "stats_per_user": stats_per_user,
        "stats_per_month": stats_per_month,
        "stats_per_recurso": stats_per_recurso,
        "total_general": CarregaHores.objects.aggregate(total=Sum('hores'))['total'] or 0
    }
    return render(request, "carregahores/admin_stats.html", context)


# AJAX: obtener líneas válidas para un pressupost (abierto, no preu_tancat, y si user normal: de su recurso)
@login_required
@require_GET
def lineas_por_pressupost(request):
    pressupost_id = request.GET.get("pressupost")
    if not pressupost_id:
        return JsonResponse([], safe=False)

    lineas = pressupost_models.PressupostLinia.objects.filter(
        pressupost_id=pressupost_id,
        preu_tancat=False,
        pressupost__tancat=False
    )

    if not request.user.is_superuser:
        perfil = getattr(request.user, "perfil", None)
        if not perfil or not perfil.recurso_id:
            return JsonResponse([], safe=False)
        lineas = lineas.filter(recurs_id=perfil.recurso_id)

    data = [{
        "id": l.pk,
        "label": f"{l.treball.descripcio} / {l.tasca.tasca} · rec: {l.recurs.nom}"
    } for l in lineas]

    return JsonResponse(data, safe=False)
