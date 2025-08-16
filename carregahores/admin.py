from django.contrib import admin
from .models import PerfilUsuario, CarregaHores

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "recurso")
    search_fields = ("user__username", "recurso__name")

@admin.register(CarregaHores)
class CarregaHoresAdmin(admin.ModelAdmin):
    list_display = ("data", "usuari", "recurso", "pressupost", "treball", "tasca", "hores")
    list_filter = ("recurso", "pressupost", "treball", "tasca", "data")
    search_fields = ("usuari__username", "observacions")
