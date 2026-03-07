from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .forms import CarregaHoresForm
from .models import CarregaHores
from pressupostos import models as pressupost_models
from projectes.models import Projecte

# Helper functions simplificadas para permisos
def is_admin(user):
    """Verifica si el usuario es administrador - SIMPLIFICADO"""
    return (user.is_authenticated and 
            (user.is_superuser or user.is_staff or 
             user.groups.filter(name='Administradores').exists()))

def get_user_recurso(user):
    """Obtiene el recurso asignado al usuario - SIMPLIFICADO"""
    try:
        return user.perfil.recurso
    except:
        return None

def can_access_pressupost(user, pressupost):
    """Verifica si un usuario puede acceder a un presupuesto - SIMPLIFICADO"""
    if is_admin(user):
        return True
    
    recurso = get_user_recurso(user)
    if not recurso:
        return False
    
    # Verificar que tenga líneas asignadas en este presupuesto
    return pressupost.linies.filter(recurs=recurso).exists()

def can_edit_carrega(user, carrega):
    """Verifica permisos de edición - SIMPLIFICADO"""
    # Admin puede todo
    if is_admin(user):
        return True
    
    # Solo el propietario puede editar (dentro de 24h)
    if carrega.usuari != user:
        return False
    
    from django.utils import timezone
    from datetime import timedelta
    
    tiempo_limite = carrega.creat + timedelta(hours=24)
    return timezone.now() <= tiempo_limite

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
def editar_carrega(request, pk):
    """
    Vista para editar una carga de horas.
    Solo el propietario (dentro de 24h) o administradores pueden editar.
    """
    carrega = get_object_or_404(CarregaHores, pk=pk)
    
    # Verificar permisos
    if not can_edit_carrega(request.user, carrega):
        messages.error(request, 'No tens permisos per editar aquest registre.')
        return redirect('carregahores:meves')
    
    if request.method == "POST":
        form = CarregaHoresForm(request.POST, instance=carrega, user=request.user)
        if form.is_valid():
            try:
                ch = form.save()
                messages.success(request, f'Càrrega d\'hores actualitzada correctament: {ch.hores} hores el {ch.data.strftime("%d/%m/%Y")}')
                return redirect("carregahores:meves")
            except Exception as e:
                messages.error(request, f"Error al actualitzar: {str(e)}")
        else:
            # Mostrar errores de validación
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CarregaHoresForm(instance=carrega, user=request.user)
    
    context = {
        'form': form,
        'carrega': carrega,
        'is_edit': True
    }
    return render(request, "carregahores/form.html", context)


@login_required
@require_POST
def eliminar_carrega(request, pk):
    """
    Vista para eliminar una carga de horas.
    Solo el propietario (dentro de 24h) o administradores pueden eliminar.
    """
    carrega = get_object_or_404(CarregaHores, pk=pk)
    
    # Verificar permisos
    if not can_edit_carrega(request.user, carrega):
        messages.error(request, 'No tens permisos per eliminar aquest registre.')
        return redirect('carregahores:meves')
    
    try:
        data_str = carrega.data.strftime('%d/%m/%Y')
        hores = carrega.hores
        carrega.delete()
        messages.success(request, f'Càrrega d\'hores eliminada correctament: {hores} hores del {data_str}')
    except Exception as e:
        messages.error(request, f"Error al eliminar: {str(e)}")
    
    return redirect('carregahores:meves')


@login_required
def meves_carregues(request):
    from django.db.models import Sum
 
    # Vista personal: solo registros del usuario autenticado
    qs = CarregaHores.objects.filter(usuari=request.user)
    title = "🎯 Les meves càrregues d'hores"
    help_text = f"Mostrant només les teves càrregues d'hores, {request.user.get_full_name() or request.user.username}."
    
    # Verificar si es admin para mostrar enlace a vista completa
    is_admin = request.user.is_superuser or request.user.is_staff
    
    # Crear formulario de filtros (sin filtro de usuario para vista personal)
    from .filters import CarreguesFilterForm
    filter_form = CarreguesFilterForm(request.GET, user=request.user, show_user_filter=False)
    
    # Aplicar filtros si el formulario es válido
    if filter_form.is_valid():
        filters = filter_form.get_queryset_filters()
        qs = qs.filter(**filters)
    
    # Ordenar por fecha descendente
    qs = qs.order_by('-data', '-creat')
    
    # Calcular total de horas del usuario
    total_hores = qs.aggregate(total=Sum('hores'))['total'] or 0
    
    # Calcular estadísticas del usuario actual
    total_registres = qs.count()
    
    context = {
        'carregues': qs,
        'total_hores': total_hores,
        'total_registres': total_registres,
        'title': title,
        'help_text': help_text,
        'is_admin': is_admin,
        'filter_form': filter_form,
        'stats': {},  # Mantener por compatibilidad
    }
    return render(request, "carregahores/list.html", context)


# Vista solo para administradores - ver TODAS las cargas
@user_passes_test(is_admin, login_url='/admin/login/')
def totes_carregues_admin(request):
    from django.db.models import Sum
    
    # QuerySet inicial con todas las cargas
    qs = CarregaHores.objects.all().select_related('usuari', 'pressupost', 'linia__recurs', 'linia__treball', 'linia__tasca')
    
    # Crear formulario de filtros (CON filtro de usuario para vista admin)
    from .filters import CarreguesFilterForm
    filter_form = CarreguesFilterForm(request.GET, user=request.user, show_user_filter=True)
    
    # Aplicar filtros si el formulario es válido
    if filter_form.is_valid():
        filters = filter_form.get_queryset_filters()
        qs = qs.filter(**filters)
    
    # Ordenar por fecha descendente
    qs = qs.order_by('-data', '-creat')
    
    # Calcular totales
    total_hores = qs.aggregate(total=Sum('hores'))['total'] or 0
    
    context = {
        "carregues": qs,  # Usar 'carregues' como en la vista normal
        "total_hores": total_hores,
        "total_registres": qs.count(),
        "is_admin_view": True,
        "filter_form": filter_form,
        "title": "🛡️ Totes les Càrregues d'Hores - Admin",
        "help_text": "Vista d'administrador: Pots veure totes les càrregues de tots els usuaris."
    }
    return render(request, "carregahores/admin_list.html", context)


# Vista solo para administradores - estadísticas
@user_passes_test(is_admin, login_url='/admin/login/')
def estadistiques_admin(request):
    from django.db.models import Sum, Count, Q
    from django.db.models.functions import TruncMonth
    from .forms import EstadistiquesFilterForm
    
    # Crear formulario de filtros
    filter_form = EstadistiquesFilterForm(request.GET or None)
    
    # Base queryset
    queryset = CarregaHores.objects.all()
    
    #Aplicar filtros si el formulario es válido
    if filter_form.is_valid():
        # Filtro por año
        if filter_form.cleaned_data.get('any'):
            queryset = queryset.filter(data__year=filter_form.cleaned_data['any'])
        
        # Filtro por mes
        if filter_form.cleaned_data.get('mes'):
            queryset = queryset.filter(data__month=filter_form.cleaned_data['mes'])
        
        # Filtro por cliente
        if filter_form.cleaned_data.get('client'):
            queryset = queryset.filter(pressupost__client=filter_form.cleaned_data['client'])
        
        # Filtro por proyecto
        if filter_form.cleaned_data.get('projecte'):
            queryset = queryset.filter(pressupost__projecte=filter_form.cleaned_data['projecte'])
        
        # Filtro por presupuesto
        if filter_form.cleaned_data.get('pressupost'):
            queryset = queryset.filter(pressupost=filter_form.cleaned_data['pressupost'])
        
        # Filtro por recurso
        if filter_form.cleaned_data.get('recurs'):
            queryset = queryset.filter(linia__recurs=filter_form.cleaned_data['recurs'])
        
        # Filtro por usuario
        if filter_form.cleaned_data.get('usuari'):
            queryset = queryset.filter(usuari=filter_form.cleaned_data['usuari'].user)
    
    # Estadísticas por usuario (con filtros aplicados)
    stats_per_user = queryset.values('usuari__username', 'usuari__first_name', 'usuari__last_name').annotate(
        total_hores=Sum('hores'),
        total_registres=Count('id')
    ).order_by('-total_hores')
    
    # Estadísticas por mes (con filtros aplicados)
    stats_per_month = queryset.annotate(
        mes=TruncMonth('data')
    ).values('mes').annotate(
        total_hores=Sum('hores'),
        total_registres=Count('id')
    ).order_by('-mes')
    
    # Estadísticas por recurso (con filtros aplicados)
    stats_per_recurso = queryset.values('linia__recurs__nom').annotate(
        total_hores=Sum('hores'),
        total_registres=Count('id')
    ).order_by('-total_hores')
    
    # Estadísticas por cliente (con filtros aplicados)
    stats_per_client = queryset.values('pressupost__client__nom_client').annotate(
        total_hores=Sum('hores'),
        total_registres=Count('id')
    ).order_by('-total_hores')
    
    # Estadísticas por proyecto (con filtros aplicados)
    stats_per_projecte = queryset.values('pressupost__projecte__nom').annotate(
        total_hores=Sum('hores'),
        total_registres=Count('id')
    ).order_by('-total_hores')
    
    context = {
        "filter_form": filter_form,
        "stats_per_user": stats_per_user,
        "stats_per_month": stats_per_month,
        "stats_per_recurso": stats_per_recurso,
        "stats_per_client": stats_per_client,
        "stats_per_projecte": stats_per_projecte,
        "total_general": queryset.aggregate(total=Sum('hores'))['total'] or 0,
        "total_registres": queryset.count()
    }
    return render(request, "carregahores/admin_stats.html", context)


# AJAX: obtener líneas válidas para un pressupost (con permisos aplicados)
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

    # 🔐 APLICAR FILTROS SEGÚN PERMISOS
    is_admin = request.user.is_superuser or request.user.is_staff
    
    lineas = pressupost_models.PressupostLinia.objects.filter(
        pressupost_id=pressupost_id,
        preu_tancat=False,
        pressupost__tancat=False
    ).select_related('treball', 'tasca', 'recurs')

    if not is_admin:
        # 👤 USUARIO NORMAL: Solo líneas de su recurso
        perfil = getattr(request.user, "perfil", None)
        if not perfil or not perfil.recurso:
            return JsonResponse({"error": "No tens un recurs assignat. Contacta amb l'administrador."}, status=403)
        
        lineas = lineas.filter(recurs=perfil.recurso)
        
        # Verificar que tiene acceso a este presupuesto
        if not lineas.exists():
            return JsonResponse({"error": "No tens línies assignades en aquest pressupost."}, status=403)

    # Preparar datos para el JSON
    lineas_data = []
    for l in lineas:
        # Asegurar que el recurso no sea None
        recurso_nom = l.recurs.nom if l.recurs else "Sense recurs"
        
        # Formato más claro para el dropdown - siempre mostrar recurso primero
        if is_admin:
            detall = f"{recurso_nom} | {l.treball.descripcio} | {l.tasca.tasca}"
        else:
            detall = f"{recurso_nom} | {l.treball.descripcio} | {l.tasca.tasca}"
            
        lineas_data.append({
            "id": l.pk,
            "detall": detall,
            "recurso": recurso_nom,
            "treball": l.treball.descripcio,
            "tasca": l.tasca.tasca
        })

    return JsonResponse({"lineas": lineas_data})


@login_required
@require_GET
def get_pressupostos_data(request):
    """
    Vista AJAX para obtener datos de presupuestos con información de cliente y proyecto
    para el filtrado dinámico
    """
    try:
        is_admin = request.user.is_superuser or request.user.is_staff
        
        if is_admin:
            # 👑 ADMIN: Todos los presupuestos abiertos
            pressupostos = pressupost_models.Pressupost.objects.filter(tancat=False).select_related(
                'client', 'projecte'
            )
        else:
            # 👤 USUARIO NORMAL: Solo presupuestos donde está asignado
            perfil = getattr(request.user, "perfil", None)
            if not perfil or not perfil.recurso:
                return JsonResponse({"error": "No tens un recurs assignat"}, status=403)
            
            pressupostos = pressupost_models.Pressupost.objects.filter(
                tancat=False,
                linies__recurs=perfil.recurso
            ).select_related('client', 'projecte').distinct()
        
        # Preparar datos para JavaScript
        data = []
        for p in pressupostos:
            data.append({
                "id": p.pk,
                "nom": p.nom or f"Pressupost {p.pk}",
                "client_id": p.client.pk if p.client else None,
                "client_nom": p.client.nom_client if p.client else "Sense client",
                "projecte_id": p.projecte.pk if p.projecte else None,
                "projecte_nom": p.projecte.nom if p.projecte else "Sense projecte"
            })
        
        return JsonResponse(data, safe=False)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_GET
def get_projectes_by_client(request):
    """
    Vista AJAX para obtener proyectos filtrados por cliente
    """
    try:
        client_id = request.GET.get('client_id')
        if not client_id:
            return JsonResponse({"error": "client_id requerido"}, status=400)
        
        is_admin = request.user.is_superuser or request.user.is_staff
        
        # Base queryset de proyectos del cliente
        projectes_qs = Projecte.objects.filter(client_id=client_id)
        
        if not is_admin:
            # 👤 USUARIO NORMAL: Solo proyectos donde tiene presupuestos asignados
            perfil = getattr(request.user, "perfil", None)
            if not perfil or not perfil.recurso:
                return JsonResponse({"error": "No tens un recurs assignat"}, status=403)
            
            # Filtrar solo proyectos donde el usuario tiene presupuestos asignados
            projectes_qs = projectes_qs.filter(
                pressupost__tancat=False,
                pressupost__linies__recurs=perfil.recurso
            ).distinct()
        
        # Preparar datos
        data = []
        for p in projectes_qs:
            data.append({
                "id": p.pk,
                "nom": p.nom,
                "client_id": p.client_id
            })
        
        return JsonResponse(data, safe=False)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_GET
def get_pressupostos_by_filters(request):
    """
    Vista AJAX para obtener presupuestos filtrados por cliente y/o proyecto
    """
    try:
        client_id = request.GET.get('client_id')
        projecte_id = request.GET.get('projecte_id')
        
        is_admin = request.user.is_superuser or request.user.is_staff
        
        if is_admin:
            # 👑 ADMIN: Todos los presupuestos abiertos
            pressupostos_qs = pressupost_models.Pressupost.objects.filter(tancat=False)
        else:
            # 👤 USUARIO NORMAL: Solo presupuestos donde está asignado
            perfil = getattr(request.user, "perfil", None)
            if not perfil or not perfil.recurso:
                return JsonResponse({"error": "No tens un recurs assignat"}, status=403)
            
            pressupostos_qs = pressupost_models.Pressupost.objects.filter(
                tancat=False,
                linies__recurs=perfil.recurso
            ).distinct()
        
        # Aplicar filtros
        if client_id:
            pressupostos_qs = pressupostos_qs.filter(client_id=client_id)
        
        if projecte_id:
            pressupostos_qs = pressupostos_qs.filter(projecte_id=projecte_id)
        
        # Preparar datos con información de cliente y proyecto
        pressupostos_qs = pressupostos_qs.select_related('client', 'projecte')
        
        data = []
        for p in pressupostos_qs:
            data.append({
                "id": p.pk,
                "nom": p.nom or f"Pressupost {p.pk}",
                "client_id": p.client.pk if p.client else None,
                "client_nom": p.client.nom_client if p.client else "Sense client",
                "projecte_id": p.projecte.pk if p.projecte else None,
                "projecte_nom": p.projecte.nom if p.projecte else "Sense projecte"
            })
        
        return JsonResponse(data, safe=False)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_GET
def get_projectes_for_stats(request):
    """
    Vista AJAX para obtener proyectos por cliente en estadísticas
    """
    try:
        client_id = request.GET.get('client_id')
        
        if client_id:
            projectes = Projecte.objects.filter(client_id=client_id).values('id', 'nom').order_by('nom')
        else:
            projectes = Projecte.objects.all().values('id', 'nom').order_by('nom')
        
        return JsonResponse(list(projectes), safe=False)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_GET
def get_pressupostos_for_stats(request):
    """
    Vista AJAX para obtener presupuestos por proyecto en estadísticas
    """
    try:
        projecte_id = request.GET.get('projecte_id')
        
        if projecte_id:
            from pressupostos.models import Pressupost
            pressupostos = Pressupost.objects.filter(projecte_id=projecte_id).values('id', 'nom').order_by('-data')
        else:
            from pressupostos.models import Pressupost
            pressupostos = Pressupost.objects.all().values('id', 'nom').order_by('-data')
        
        return JsonResponse(list(pressupostos), safe=False)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def test_ajax_view(request):
    """Vista simple para testing AJAX"""
    return render(request, 'test_ajax.html')
