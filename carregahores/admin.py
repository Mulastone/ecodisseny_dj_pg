from django.contrib import admin
from .models import CarregaHores


@admin.register(CarregaHores)
class CarregaHoresAdmin(admin.ModelAdmin):
    list_display = ("data", "mostrar_usuari", "get_recurso", "mostrar_pressupost", "get_treball", "get_tasca", "hores")
    list_filter = ("linia__recurs", "pressupost", "linia__treball", "linia__tasca", "data", "usuari")
    search_fields = ("usuari__username", "usuari__first_name", "usuari__last_name", "observacions")
    date_hierarchy = "data"
    ordering = ["-data", "-creat"]
    
    @admin.display(description="Usuari")
    def mostrar_usuari(self, obj):
        return obj.usuari.get_full_name() or obj.usuari.username
    
    @admin.display(description="Pressupost")
    def mostrar_pressupost(self, obj):
        return f"{obj.pressupost.nom} ({obj.pressupost.client.nom_client})"
    
    @admin.display(description="Recurs", ordering="linia__recurs__nom")
    def get_recurso(self, obj):
        return obj.recurso.nom if obj.recurso else "-"
    
    @admin.display(description="Treball", ordering="linia__treball__descripcio") 
    def get_treball(self, obj):
        return obj.treball.descripcio if obj.treball else "-"
    
    @admin.display(description="Tasca", ordering="linia__tasca__tasca")
    def get_tasca(self, obj):
        return obj.tasca.tasca if obj.tasca else "-"
    
    def get_queryset(self, request):
        """Aplicar filtros según permisos del admin"""
        qs = super().get_queryset(request)
        
        # Si no es superuser, solo ve sus propios registros
        if not request.user.is_superuser:
            qs = qs.filter(usuari=request.user)
        
        return qs.select_related('usuari', 'pressupost', 'linia__recurs', 'linia__treball', 'linia__tasca')
    
    def has_change_permission(self, request, obj=None):
        """Solo admin o propietario pueden editar"""
        if request.user.is_superuser:
            return True
        if obj and obj.usuari == request.user:
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo admin o propietario pueden eliminar"""
        return self.has_change_permission(request, obj)
