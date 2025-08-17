from django.urls import path
from . import views

app_name = 'documentacion'

urlpatterns = [
    # Página principal de documentación
    path('', views.index_documentacion, name='index'),
    
    # Búsqueda global
    path('buscar/', views.busqueda_global, name='busqueda'),
    
    # Analytics (solo administradores)
    path('analytics/', views.AnalyticsDocumentacion.as_view(), name='analytics'),
    
    # Feedback AJAX
    path('feedback/<int:documento_id>/', views.feedback_documento, name='feedback'),
    
    # Documentos por categoría
    path('<slug:categoria_slug>/', views.lista_categoria, name='categoria'),
    
    # Documento específico
    path('<slug:categoria_slug>/<slug:documento_slug>/', 
         views.detalle_documento, name='documento'),
]
