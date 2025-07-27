from django.contrib import admin, messages
from django.db import IntegrityError
from django.core.exceptions import ValidationError


def safe_delete_selected_action(modeladmin, request, queryset):
    """
    Acción segura de eliminación en el admin. 
    Evita IntegrityError y muestra mensajes personalizados.
    """
    eliminats = []
    errors = []

    for obj in queryset:
        try:
            obj.delete()
            eliminats.append(str(obj))
        except (IntegrityError, ValidationError):
            errors.append(str(obj))

    label_singular = getattr(modeladmin, 'delete_model_label', 'element')
    label_plural = getattr(modeladmin, 'delete_model_label_plural', f"{label_singular}s")

    if eliminats:
        modeladmin.message_user(
            request,
            f"S'han eliminat correctament {len(eliminats)} {label_plural}: {', '.join(eliminats)}.",
            level=messages.SUCCESS
        )
    if errors:
        for name in errors:
            modeladmin.message_user(
                request,
                f"No es pot eliminar '{name}' perquè est\u00e0 en \u00fas.",
                level=messages.ERROR
            )


class SafeDeleteAdmin(admin.ModelAdmin):
    """
    Admin base que desactiva la eliminació múltiple por defecto
    y reemplaza por una versión segura.
    """
    actions = [safe_delete_selected_action]

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions
