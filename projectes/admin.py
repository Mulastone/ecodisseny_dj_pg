from django.contrib import admin
from .models import Projecte
from .forms import ProjectesForm


@admin.register(Projecte)
class ProjecteAdmin(admin.ModelAdmin):
    form = ProjectesForm
    list_display = ("nom", "mostrar_client", "tancat", "data_peticio")
    search_fields = ("nom", "client__nom_client", "persona_contacte__nom_contacte")
    list_filter = ("tancat", "parroquia", "client")

    @admin.display(description="Client", ordering="client__nom_client")
    def mostrar_client(self, obj):
        return obj.client.nom_client if obj.client else "-"

    @admin.display(description="Departament", ordering="departament__nom")
    def mostrar_departament(self, obj):
        return obj.departament.nom if obj.departament else "-"
