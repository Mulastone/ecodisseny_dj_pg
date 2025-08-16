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
    import logging
    logger = logging.getLogger(__name__)
    
    if request.method == "POST":
        print(f"🔍 POST data received: {dict(request.POST)}")
        logger.info(f"🔍 POST data received: {dict(request.POST)}")
        
        form = CarregaHoresForm(request.POST, user=request.user)
        
        print(f"🔍 Form is_valid: {form.is_valid()}")
        logger.info(f"🔍 Form is_valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"🔍 Form errors: {form.errors}")
            logger.error(f"🔍 Form errors: {form.errors}")
            logger.error(f"🔍 Form non_field_errors: {form.non_field_errors}")
        
        if form.is_valid():
            try:
                ch = form.save(commit=False)
                ch.usuari = request.user
                logger.info(f"🔍 About to save: hores={ch.hores}, linia={ch.linia}, pressupost={ch.pressupost}")
                ch.save()
                messages.success(request, f"Càrrega d'hores guardada correctament: {ch.hores} hores el {ch.data.strftime('%d/%m/%Y')}")
                return redirect("carregahores:meves")
            except Exception as e:
                logger.error(f"🔍 Save error: {str(e)}")
                messages.error(request, f"Error al guardar: {str(e)}")
        else:
            # Mostrar errores de validación del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    logger.error(f"🔍 Form error - {field}: {error}")
                    messages.error(request, f"{field}: {error}")
    else:
        form = CarregaHoresForm(user=request.user)
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
    
    qs = CarregaHores.objects.all().select_related('usuari', 'pressupost', 'linia__recurs', 'linia__treball', 'linia__tasca')
    
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
    stats_per_recurso = CarregaHores.objects.values('linia__recurs__nom').annotate(
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

    try:
        pressupost = pressupost_models.Pressupost.objects.get(pk=pressupost_id)
        if pressupost.tancat:
            return JsonResponse({"error": "El pressupost està tancat"}, status=400)
    except pressupost_models.Pressupost.DoesNotExist:
        return JsonResponse({"error": "Pressupost no trobat"}, status=404)

    lineas = pressupost_models.PressupostLinia.objects.filter(
        pressupost_id=pressupost_id,
        preu_tancat=False,
        pressupost__tancat=False
    ).select_related('treball', 'tasca', 'recurs')

    # Filtrar por recurso del usuario si no es admin
    if not request.user.is_superuser:
        perfil = getattr(request.user, "perfil", None)
        if not perfil or not perfil.recurso_id:
            return JsonResponse({"error": "No tens un recurs assignat"}, status=403)
        lineas = lineas.filter(recurs_id=perfil.recurso_id)

    # Preparar datos para el JSON
    data = []
    for l in lineas:
        data.append({
            "id": l.pk,
            "label": f"{l.treball.descripcio} | {l.tasca.tasca}",
            "recurso": l.recurs.nom,
            "detall": f"Recurs: {l.recurs.nom} | Treball: {l.treball.descripcio} | Tasca: {l.tasca.tasca}"
        })

    return JsonResponse(data, safe=False)
