from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from .models import (
    Clients, Parroquia, Poblacio, Recurso, TipusRecurso,
    Tasca, Treball, Ubicacio, TasquesTreball, Desplacament,
    Hores, DepartamentClient, PersonaContactClient
)
from .forms import ClientAdminForm
from .admin_utils import SafeDeleteAdmin


@admin.register(Clients)
class ClientsAdmin(admin.ModelAdmin):
    form = ClientAdminForm
    list_display = ("nom_client", "mail", "telefon", "nrt")
    search_fields = ("nom_client", "mail", "nrt")
    fieldsets = (
        ("Informació general", {
            'fields': ('nom_client', 'rao_social', 'nrt', 'telefon', 'mail')
        }),
        ("Adreça", {
            'fields': ('parroquia', 'poblacio', 'carrer', 'numero', 'escala', 'pis', 'porta'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Parroquia)
class ParroquiaAdmin(admin.ModelAdmin):
    list_display = ("parroquia",)
    search_fields = ("parroquia",)


class ParroquiaFilter(SimpleListFilter):
    title = 'Parròquia'
    parameter_name = 'parroquia'

    def lookups(self, request, model_admin):
        return [(p.id, p.parroquia) for p in Parroquia.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(parroquia_id=self.value())
        return queryset


@admin.register(Poblacio)
class PoblacioAdmin(admin.ModelAdmin):
    list_display = ("poblacio", "codi_postal", "mostrar_parroquia")
    list_filter = (ParroquiaFilter,)
    search_fields = ("poblacio",)
    list_per_page = 10

    @admin.display(description="Parròquia")
    def mostrar_parroquia(self, obj):
        return obj.parroquia.parroquia if obj.parroquia else "-"


@admin.register(TipusRecurso)
class TipusRecursoAdmin(admin.ModelAdmin):
    list_display = ("tipus",)
    search_fields = ("tipus",)


class TipusRecursoFilter(SimpleListFilter):
    title = 'Tipus de Recurs'
    parameter_name = 'tipus_recurso'

    def lookups(self, request, model_admin):
        return [(t.id, t.tipus) for t in TipusRecurso.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tipus_recurso_id=self.value())
        return queryset


@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display = ("nom", "mostrar_tipus", "preu_tancat", "preu_hora")
    list_filter = (TipusRecursoFilter, "preu_tancat")
    search_fields = ("nom",)

    @admin.display(description="Tipus", ordering="tipus_recurso__tipus")
    def mostrar_tipus(self, obj):
        return obj.tipus_recurso.tipus if obj.tipus_recurso else "-"


@admin.register(Treball)
class TreballAdmin(admin.ModelAdmin):
    list_display = ("descripcio",)
    search_fields = ("descripcio",)


@admin.register(Tasca)
class TascaAdmin(admin.ModelAdmin):
    list_display = ("tasca",)
    search_fields = ("tasca",)


@admin.register(Ubicacio)
class UbicacioAdmin(admin.ModelAdmin):
    list_display = ("ubicacio",)
    search_fields = ("ubicacio",)


class TascaFilter(SimpleListFilter):
    title = 'Tasca'
    parameter_name = 'tasca'

    def lookups(self, request, model_admin):
        return [(t.id, t.tasca) for t in Tasca.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tasca_id=self.value())
        return queryset


class TreballFilter(SimpleListFilter):
    title = 'Treball'
    parameter_name = 'treball'

    def lookups(self, request, model_admin):
        return [(t.id, t.descripcio) for t in Treball.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(treball_id=self.value())
        return queryset


@admin.register(TasquesTreball)
class TasquesTreballAdmin(admin.ModelAdmin):
    list_display = ("mostrar_tasca", "mostrar_treball", "observacions")
    list_filter = (TascaFilter, TreballFilter)
    search_fields = ("tasca__tasca", "treball__descripcio")

    @admin.display(description="Tasca")
    def mostrar_tasca(self, obj):
        return obj.tasca.tasca if obj.tasca else "-"

    @admin.display(description="Treball")
    def mostrar_treball(self, obj):
        return obj.treball.descripcio if obj.treball else "-"


class UbicacioFilter(SimpleListFilter):
    title = 'Ubicació'
    parameter_name = 'ubicacio'

    def lookups(self, request, model_admin):
        return [(u.id, u.ubicacio) for u in Ubicacio.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(ubicacio_id=self.value())
        return queryset


@admin.register(Desplacament)
class DesplacamentAdmin(admin.ModelAdmin):
    list_display = ("mostrar_parroquia", "mostrar_ubicacio", "mostrar_tasca", "increment_hores")
    list_filter = (ParroquiaFilter, UbicacioFilter, TascaFilter)
    search_fields = ("parroquia__parroquia", "ubicacio__ubicacio", "tasca__tasca")
    ordering = ["-data_creacio"]
    list_per_page = 10

    @admin.display(description="Parròquia")
    def mostrar_parroquia(self, obj):
        return obj.parroquia.parroquia if obj.parroquia else "-"

    @admin.display(description="Ubicació")
    def mostrar_ubicacio(self, obj):
        return obj.ubicacio.ubicacio if obj.ubicacio else "-"

    @admin.display(description="Tasca")
    def mostrar_tasca(self, obj):
        return obj.tasca.tasca if obj.tasca else "-"


@admin.register(Hores)
class HoresAdmin(admin.ModelAdmin):
    list_display = ("hores",)
    search_fields = ("hores",)
    ordering = ["hores"]
    list_per_page = 10


@admin.register(DepartamentClient)
class DepartamentClientAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)
    list_filter = ("nom",)
    ordering = ["nom"]
    list_per_page = 10


class ClientFilter(SimpleListFilter):
    title = 'Client'
    parameter_name = 'client'

    def lookups(self, request, model_admin):
        return [(c.id, c.nom_client) for c in Clients.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(client_id=self.value())
        return queryset


@admin.register(PersonaContactClient)
class PersonaContactClientAdmin(SafeDeleteAdmin):
    list_display = ("nom_contacte", "mostrar_client", "telefon")
    list_filter = (ClientFilter,)
    search_fields = ("nom_contacte",)
    list_per_page = 10

    delete_model_label = "contacte"
    delete_model_label_plural = "contactes"

    @admin.display(description="Client")
    def mostrar_client(self, obj):
        return obj.client.nom_client if obj.client else "-"
