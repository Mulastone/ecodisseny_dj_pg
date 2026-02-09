from django.contrib import admin
from django.contrib import messages
from django.db.models import ProtectedError
from .models import Projecte
from .forms import ProjectesForm


@admin.register(Projecte)
class ProjecteAdmin(admin.ModelAdmin):
    form = ProjectesForm
    list_display = ("nom", "mostrar_client", "tancat", "data_peticio")
    search_fields = ("nom", "client__nom_client", "persona_contacte__nom_contacte")
    list_filter = ("tancat", "parroquia", "client")
    
    class Media:
        # Asegurar que se carguen los archivos necesarios para autocomplete
        pass

    @admin.display(description="Client", ordering="client__nom_client")
    def mostrar_client(self, obj):
        return obj.client.nom_client if obj.client else "-"

    @admin.display(description="Departament", ordering="departament__nom")
    def mostrar_departament(self, obj):
        return obj.departament.nom if obj.departament else "-"
    
    def delete_model(self, request, obj):
        try:
            obj.delete()
        except ProtectedError as e:
            messages.error(
                request,
                f"No es pot eliminar el projecte '{obj.nom}' perquè té pressupostos associats. "
                "Elimina primer els pressupostos relacionats."
            )
            return
    
    def delete_queryset(self, request, queryset):
        try:
            queryset.delete()
        except ProtectedError as e:
            messages.error(
                request,
                "No es poden eliminar alguns projectes perquè tenen pressupostos associats. "
                "Elimina primer els pressupostos relacionats."
            )
