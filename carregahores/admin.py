from django.contrib import admin
from .models import PerfilUsuario, CarregaHores

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "recurso")
    search_fields = ("user__username", "recurso__name")

@admin.register(CarregaHores)
class CarregaHoresAdmin(admin.ModelAdmin):
    list_display = ("data", "usuari", "get_recurso", "pressupost", "get_treball", "get_tasca", "hores")
    list_filter = ("linia__recurs", "pressupost", "linia__treball", "linia__tasca", "data")
    search_fields = ("usuari__username", "observacions")
    
    @admin.display(description="Recurs")
    def get_recurso(self, obj):
        return obj.recurso.nom if obj.recurso else "-"
    
    @admin.display(description="Treball") 
    def get_treball(self, obj):
        return obj.treball.descripcio if obj.treball else "-"
    
    @admin.display(description="Tasca")
    def get_tasca(self, obj):
        return obj.tasca.tasca if obj.tasca else "-"
