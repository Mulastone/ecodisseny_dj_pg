from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib import messages
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django import forms
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
    change_form_template = 'admin/maestros/clients_change_form.html'
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

    def save_model(self, request, obj, form, change):
        from django.db import IntegrityError
        try:
            super().save_model(request, obj, form, change)
        except IntegrityError as e:
            if 'nom_client' in str(e) and 'unique' in str(e).lower():
                messages.error(
                    request,
                    f"❌ Ja existeix un client amb el nom '{obj.nom_client}'. "
                    "Els noms de client han de ser únics."
                )
            else:
                messages.error(request, f"Error d'integritat: {str(e)}")
            # No guardar si hay error
            return

    def delete_model(self, request, obj):
        try:
            obj.delete()
        except ProtectedError as e:
            messages.error(
                request,
                f"No es pot eliminar el client '{obj.nom_client}' perquè té projectes o pressupostos associats. "
                "Elimina primer els elements relacionats."
            )
            return

    def delete_queryset(self, request, queryset):
        try:
            queryset.delete()
        except ProtectedError as e:
            messages.error(
                request,
                "No es poden eliminar alguns clients perquè tenen projectes o pressupostos associats. "
                "Elimina primer els elements relacionats."
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
    list_display = ("nom", "mostrar_tipus", "necessita_usuari", "preu_tancat", "preu_hora")
    list_filter = (TipusRecursoFilter, "preu_tancat")
    search_fields = ("nom",)

    @admin.display(description="Tipus", ordering="tipus_recurso__tipus")
    def mostrar_tipus(self, obj):
        return obj.tipus_recurso.tipus if obj.tipus_recurso else "-"

    @admin.display(description="Necessita Usuari", boolean=True)
    def necessita_usuari(self, obj):
        return obj.necesita_usuario


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


class IncrementHoresFilter(SimpleListFilter):
    title = 'Increment d\'Hores'
    parameter_name = 'increment_hores'

    def lookups(self, request, model_admin):
        # Obtener valores únicos de increment_hores de la base de datos
        values = Desplacament.objects.values_list('increment_hores', flat=True).distinct().order_by('increment_hores')
        choices = []

        # Añadir filtro especial para valores distintos de 0
        choices.append(('no_zero', 'Amb increment (≠ 0)'))

        # Añadir filtros por valores exactos que existen en la BD
        for value in values:
            if value is not None:
                if value == 0:
                    choices.append((str(value), '{} hores (sense increment)'.format(value)))
                elif value == 0.5:
                    choices.append((str(value), '{} hores (mitja hora)'.format(value)))
                elif value == int(value):
                    choices.append((str(value), '{} hores'.format(int(value))))
                else:
                    choices.append((str(value), '{} hores'.format(value)))

        # Añadir filtros por rangos si hay suficients dades
        if values:
            choices.extend([
                ('0-1', '0 - 1 hora'),
                ('1-2', '1 - 2 hores'),
                ('2+', 'Més de 2 hores'),
            ])

        return choices

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'no_zero':
            # Filtro especial: todos los valores distintos de 0
            return queryset.exclude(increment_hores=0)
        elif value and value.replace('.', '').replace('-', '').isdigit():
            # Filtro por valor exacto
            try:
                exact_value = float(value)
                return queryset.filter(increment_hores=exact_value)
            except ValueError:
                pass
        elif value == '0-1':
            return queryset.filter(increment_hores__gte=0, increment_hores__lt=1)
        elif value == '1-2':
            return queryset.filter(increment_hores__gte=1, increment_hores__lt=2)
        elif value == '2+':
            return queryset.filter(increment_hores__gte=2)
        return queryset


class UpdateIncrementHoresForm(forms.Form):
    # Versión simplificada para debuggear
    increment_hores = forms.DecimalField(
        label="Nou increment d'hores",
        max_digits=5,
        decimal_places=2,
        initial=0,
        help_text="Introdueix el nou valor"
    )

    def clean(self):
        cleaned_data = super().clean()
        increment_hores = cleaned_data.get('increment_hores', 0)
        cleaned_data['valor_final'] = increment_hores
        return cleaned_data


def update_increment_hores(modeladmin, request, queryset):
    """Acció per actualitzar l'increment d'hores dels desplaçaments seleccionats"""
    # Versión simplificada para debuggear
    try:
        if 'apply' in request.POST:
            form = UpdateIncrementHoresForm(request.POST)
            if form.is_valid():
                increment_hores = form.cleaned_data.get('valor_final', 0)
                count = queryset.update(increment_hores=increment_hores)
                modeladmin.message_user(
                    request,
                    "Actualitzat correctament {} registres".format(count),
                    messages.SUCCESS
                )
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = UpdateIncrementHoresForm()

        # Simplified context
        context = {
            'form': form,
            'queryset': queryset,
            'action_checkbox_name': '_selected_action',
            'opts': modeladmin.model._meta,
            'title': 'Actualitzar Increment Hores',
        }

        return render(request, 'admin/update_increment_hores.html', context)

    except Exception as e:
        modeladmin.message_user(
            request,
            "Error: {}".format(str(e)),
            messages.ERROR
        )
        return HttpResponseRedirect(request.get_full_path())

update_increment_hores.short_description = "Actualitzar increment d'hores"


@admin.register(Desplacament)
class DesplacamentAdmin(admin.ModelAdmin):
    list_display = ("mostrar_parroquia", "mostrar_ubicacio", "mostrar_tasca", "increment_hores")
    list_filter = (ParroquiaFilter, UbicacioFilter, TascaFilter, IncrementHoresFilter)
    search_fields = ("parroquia__parroquia", "ubicacio__ubicacio", "tasca__tasca", "increment_hores")
    ordering = ["-data_creacio"]
    list_per_page = 10
    actions = [update_increment_hores]

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


# PerfilUsuario Admin (movido desde carregahores)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario


class PerfilUsuarioInline(admin.StackedInline):
    """Inline para gestionar el perfil desde el admin de usuarios"""
    model = PerfilUsuario
    can_delete = False
    verbose_name = "Perfil i Recurs Assignat"
    verbose_name_plural = "Perfil i Recurs Assignat"
    extra = 0
    fields = ('recurso',)


class UserAdmin(BaseUserAdmin):
    """Admin de usuarios extendido con perfil inline"""
    inlines = (PerfilUsuarioInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


# Re-registrar User admin con el perfil incluido
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("mostrar_usuario", "mostrar_recurso", "es_admin")
    list_filter = ("recurso", "user__is_staff", "user__is_superuser")
    search_fields = ("user__username", "user__first_name", "user__last_name", "recurso__nom")
    raw_id_fields = ("user",)

    @admin.display(description="Usuari", ordering="user__username")
    def mostrar_usuario(self, obj):
        name = obj.user.get_full_name() or obj.user.username
        return f"{name} (@{obj.user.username})"

    @admin.display(description="Recurs Assignat")
    def mostrar_recurso(self, obj):
        if obj.recurso:
            tipus_info = f"({obj.recurso.tipus_recurso.tipus})" if obj.recurso.tipus_recurso else ""
            if obj.recurso.es_extern:
                return f"🌐 {obj.recurso.nom} {tipus_info}"
            else:
                return f"👤 {obj.recurso.nom} {tipus_info}"
        return "❌ Sense recurs"

    @admin.display(description="Admin", boolean=True)
    def es_admin(self, obj):
        return obj.user.is_superuser or obj.user.is_staff

    fieldsets = (
        (None, {
            'fields': ('user', 'recurso'),
            'description': 'Assigna un recurs a l\'usuari per controlar els seus permisos en CarregaHores.'
        }),
    )
