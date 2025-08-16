from django.urls import path
from . import views

app_name = "carregahores"

urlpatterns = [
    # URLs públicas (para usuarios autenticados)
    path("nova/", views.nova_carrega, name="nova"),
    path("meves/", views.meves_carregues, name="meves"),
    path("ajax/lineas/", views.lineas_por_pressupost, name="ajax_lineas"),
    
    # URLs solo para administradores
    path("admin/totes/", views.totes_carregues_admin, name="admin_totes"),
    path("admin/estadistiques/", views.estadistiques_admin, name="admin_stats"),
]
