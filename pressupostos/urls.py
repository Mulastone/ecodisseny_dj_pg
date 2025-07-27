from django.urls import path
from . import views

app_name = "pressupostos"

urlpatterns = [
    # Llistat i detall
    path('', views.list_pressuposts),
    path('list/', views.list_pressuposts, name='list'),
    path('detall/<int:pk>/', views.detail_view, name='detall'),

    # Formularis CRUD
    path('form/', views.form_pressupost, name='create'),
    path('form/<int:id>/', views.form_pressupost, name='edit'),
    path('delete/<int:id>/', views.delete_pressupost, name='delete'),
    path('delete_ajax/<int:pk>/', views.eliminar_pressupost_ajax, name='delete_ajax'),


    # AJAX endpoints
    path('get_increment_hores/', views.get_increment_hores, name='get_increment_hores'),
    path('get_projectes/<int:client_id>/', views.get_projectes_by_client, name='get_projectes_by_client'),
    path('get_tasques/<int:treball_id>/', views.get_tasques_by_treball, name='get_tasques_by_treball'),
    path('get_recurso/<int:recurs_id>/', views.get_recurso_by_id, name='get_recurso'),

    # PDF
    path('pdf/<int:id>/', views.veure_pdf_pressupost, name='pdf'),
    path('<int:pressupost_id>/generar_pdf/', views.generar_pdf_y_guardar, name='generar_pdf'),
    path("delete_version_ajax/<int:version_id>/", views.delete_version_ajax, name="delete_version_ajax"),

]
