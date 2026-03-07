from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from .models import CategoriaDocumentacion, DocumentoMarkdown, HistorialAcceso, FeedbackDocumentacion


@login_required
def index_documentacion(request):
    """Vista principal de la documentación"""
    
    # Obtener categorías según permisos del usuario
    categorias = CategoriaDocumentacion.objects.filter(activa=True).annotate(
        num_documentos=Count('documentos', filter=Q(documentos__publicado=True))
    )
    categorias_permitidas = []
    
    for categoria in categorias:
        # Si no hay grupos específicos, todos pueden acceder
        if not categoria.grupos_permitidos.exists():
            categorias_permitidas.append(categoria)
        # Si pertenece a algún grupo permitido
        elif categoria.grupos_permitidos.filter(
            id__in=request.user.groups.values_list('id', flat=True)
        ).exists():
            categorias_permitidas.append(categoria)
    
    # Documentos destacados que el usuario puede ver
    documentos_destacados = []
    for categoria in categorias_permitidas:
        docs = DocumentoMarkdown.objects.filter(
            categoria=categoria,
            publicado=True,
            destacado=True
        )[:3]  # Máximo 3 por categoría
        documentos_destacados.extend(docs)
    
    # Estadísticas básicas
    total_documentos = sum(
        DocumentoMarkdown.objects.filter(
            categoria=cat, 
            publicado=True
        ).count() for cat in categorias_permitidas
    )
    
    context = {
        'categorias': categorias_permitidas,
        'documentos_destacats': documentos_destacados[:6],  # Màxim 6 total
        'total_documents': total_documentos,
        'titulo_pagina': 'Centre de Documentació',
    }
    
    return render(request, 'documentacion/index.html', context)


@login_required
def lista_categoria(request, categoria_slug):
    """Vista de documentos de una categoría específica"""
    
    categoria = get_object_or_404(CategoriaDocumentacion, slug=categoria_slug, activa=True)
    
    # Verificar permisos
    if categoria.grupos_permitidos.exists():
        if not categoria.grupos_permitidos.filter(
            id__in=request.user.groups.values_list('id', flat=True)
        ).exists():
            messages.error(request, 'No tens permisos per accedir a aquesta secció.')
            return redirect('documentacion:index')
    
    # Obtener documentos con búsqueda opcional
    documentos = DocumentoMarkdown.objects.filter(
        categoria=categoria,
        publicado=True
    )
    
    # Filtro de búsqueda
    busqueda = request.GET.get('q', '')
    if busqueda:
        documentos = documentos.filter(
            Q(titulo__icontains=busqueda) |
            Q(resumen__icontains=busqueda) |
            Q(palabras_clave__icontains=busqueda)
        )
    
    context = {
        'categoria': categoria,
        'documentos': documentos,
        'busqueda': busqueda,
        'titulo_pagina': f'Documentació - {categoria.nombre}',
    }
    
    return render(request, 'documentacion/categoria.html', context)


@login_required
def detalle_documento(request, categoria_slug, documento_slug):
    """Vista de un documento específico"""
    
    categoria = get_object_or_404(CategoriaDocumentacion, slug=categoria_slug, activa=True)
    documento = get_object_or_404(
        DocumentoMarkdown, 
        categoria=categoria, 
        slug=documento_slug,
        publicado=True
    )
    
    # Verificar permisos
    if not documento.puede_acceder(request.user):
        messages.error(request, 'No tens permisos per accedir a aquest document.')
        return redirect('documentacion:categoria', categoria_slug=categoria_slug)
    
    # Registrar acceso para analytics
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    HistorialAcceso.objects.create(
        documento=documento,
        usuario=request.user,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )
    
    # Obtener feedback existente del usuario
    feedback_usuario = FeedbackDocumentacion.objects.filter(
        documento=documento,
        usuario=request.user
    ).first()
    
    # Documentos relacionados
    documentos_relacionados = DocumentoMarkdown.objects.filter(
        categoria=categoria,
        publicado=True
    ).exclude(id=documento.id)[:5]
    
    context = {
        'categoria': categoria,
        'documento': documento,
        'contenido_html': documento.get_contenido_html(),
        'feedback_usuario': feedback_usuario,
        'documentos_relacionats': documentos_relacionados,
        'titulo_pagina': documento.titulo,
    }
    
    return render(request, 'documentacion/documento.html', context)


@login_required
@require_POST
def feedback_documento(request, documento_id):
    """Enviar feedback sobre un documento"""
    
    documento = get_object_or_404(DocumentoMarkdown, id=documento_id, publicado=True)
    
    if not documento.puede_acceder(request.user):
        return JsonResponse({'error': 'Sense permisos'}, status=403)
    
    tipo = request.POST.get('tipo')
    comentario = request.POST.get('comentario', '').strip()
    
    if tipo not in dict(FeedbackDocumentacion.TIPUS_FEEDBACK):
        return JsonResponse({'error': 'Tipus de feedback invàlid'}, status=400)
    
    # Crear o actualizar feedback
    feedback, created = FeedbackDocumentacion.objects.update_or_create(
        documento=documento,
        usuario=request.user,
        defaults={
            'tipo': tipo,
            'comentario': comentario,
            'procesado': False
        }
    )
    
    accio = 'creat' if created else 'actualitzat'
    
    return JsonResponse({
        'success': True,
        'message': f'Feedback {accio} correctament',
        'tipo': feedback.get_tipo_display()
    })


@login_required
def busqueda_global(request):
    """Búsqueda global en toda la documentación"""
    
    query = request.GET.get('q', '').strip()
    resultados = []
    
    if query and len(query) >= 3:
        # Obtener categorías permitidas para el usuario
        categorias_ids = []
        for categoria in CategoriaDocumentacion.objects.filter(activa=True):
            if not categoria.grupos_permitidos.exists():
                categorias_ids.append(categoria.id)
            elif categoria.grupos_permitidos.filter(
                id__in=request.user.groups.values_list('id', flat=True)
            ).exists():
                categorias_ids.append(categoria.id)
        
        # Buscar en documentos permitidos
        resultados = DocumentoMarkdown.objects.filter(
            categoria_id__in=categorias_ids,
            publicado=True
        ).filter(
            Q(titulo__icontains=query) |
            Q(resumen__icontains=query) |
            Q(palabras_clave__icontains=query)
        ).select_related('categoria')[:20]
    
    context = {
        'query': query,
        'resultats': resultados,
        'total_resultats': len(resultados),
        'titulo_pagina': f'Cerca: {query}' if query else 'Cerca',
    }
    
    return render(request, 'documentacion/busqueda.html', context)


class AnalyticsDocumentacion(ListView):
    """Vista de analytics para administradores"""
    
    template_name = 'documentacion/analytics.html'
    context_object_name = 'estadisticas'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # Solo para administradores
        if not request.user.is_staff:
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('documentacion:index')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return None  # No necesitamos queryset aquí
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Documentos más visitados
        documentos_populares = DocumentoMarkdown.objects.annotate(
            visitas=Count('accesos')
        ).filter(publicado=True, visitas__gt=0).order_by('-visitas')[:10]
        
        # Feedback reciente
        feedback_reciente = FeedbackDocumentacion.objects.filter(
            procesado=False
        ).order_by('-fecha')[:20]
        
        # Estadísticas por categoría
        stats_categorias = CategoriaDocumentacion.objects.annotate(
            total_docs=Count('documentos', filter=Q(documentos__publicado=True), distinct=True),
            total_visitas=Count('documentos__accesos', filter=Q(documentos__publicado=True))
        ).filter(activa=True)
        
        context.update({
            'documentos_populares': documentos_populares,
            'feedback_reciente': feedback_reciente,
            'stats_categorias': stats_categorias,
            'titulo_pagina': 'Analytics - Documentació',
        })
        
        return context
