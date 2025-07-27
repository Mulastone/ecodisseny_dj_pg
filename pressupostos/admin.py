from django.contrib import admin
from django.db.models import Sum
from .models import Pressupost, PressupostLinia
from .forms import PressupostForm


class PressupostLiniaInline(admin.TabularInline):
    model = PressupostLinia
    extra = 1
    readonly_fields = [
        'preu_tancat', 'increment_hores', 'hores_totals',
        'cost_hores', 'cost_hores_totals', 'subtotal',
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        ordering_map = {
            "hora": "hores",
            "tasca": "tasca",
            "treball": "descripcio",
            "recurs": "nom",
        }
        if db_field.name in ordering_map:
            kwargs["queryset"] = db_field.remote_field.model.objects.order_by(ordering_map[db_field.name])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        def formfield_for_dbfield(db_field, **kwargs):
            formfield = super(formset.form, formset.form).formfield_for_dbfield(db_field, **kwargs)
            if db_field.name == 'benefici':
                formfield.help_text = "Escriu un percentatge (per ex. 10 per a un 10%)"
            return formfield

        formset.form.formfield_for_dbfield = formfield_for_dbfield
        return formset


@admin.register(Pressupost)
class PressupostAdmin(admin.ModelAdmin):
    form = PressupostForm
    list_display = ("nom", "mostrar_projecte", "mostrar_client", "data", "tancat")
    search_fields = ("nom", "projecte__nom", "client__nom_client")
    list_filter = ("client", "projecte", "tancat", "data")
    inlines = [PressupostLiniaInline]
    readonly_fields = ["pressupost_total_display"]

    fieldsets = (
        (None, {
            "fields": (
                "nom", "client", "projecte", "parroquia", "ubicacio",
                "data", "tancat", "observacions", "pressupost_total_display"
            )
        }),
    )

    @admin.display(description="Total Pressupost")
    def pressupost_total_display(self, obj):
        if not obj.pk:
            return "Cal desar el pressupost primer."
        total = obj.linies.aggregate(Sum('total'))['total__sum']
        return f"{total:.2f} €" if total else "0.00 €"

    @admin.display(description="Projecte")
    def mostrar_projecte(self, obj):
        return obj.projecte.nom if obj.projecte else "-"

    @admin.display(description="Client")
    def mostrar_client(self, obj):
        return obj.client.nom_client if obj.client else "-"
