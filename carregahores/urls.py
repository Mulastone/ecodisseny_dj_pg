from django.urls import path
from . import views

app_name = "carregahores"

urlpatterns = [
    # URLs públicas (para usuarios autenticados)
    path("nova/", views.nova_carrega, name="nova"),
    path("meves/", views.meves_carregues, name="meves"),
    path("editar/<int:pk>/", views.editar_carrega, name="editar"),
    path("eliminar/<int:pk>/", views.eliminar_carrega, name="eliminar"),
    path("ajax/lineas/", views.lineas_por_pressupost, name="ajax_lineas"),
    path("ajax/pressupostos-data/", views.get_pressupostos_data, name="ajax_pressupostos_data"),
    path("ajax/projectes-by-client/", views.get_projectes_by_client, name="ajax_projectes_by_client"),
    path("ajax/pressupostos-by-filters/", views.get_pressupostos_by_filters, name="ajax_pressupostos_by_filters"),
    path("ajax/stats/projectes/", views.get_projectes_for_stats, name="ajax_stats_projectes"),
    path("ajax/stats/pressupostos/", views.get_pressupostos_for_stats, name="ajax_stats_pressupostos"),
    path("test-ajax/", views.test_ajax_view, name="test_ajax"),
    
    # URLs solo para administradores
    path("admin/totes/", views.totes_carregues_admin, name="admin_totes"),
    path("admin/estadistiques/", views.estadistiques_admin, name="admin_stats"),
]
