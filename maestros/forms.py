from dal import autocomplete
from django import forms

from .models import Clients


class ClientAdminForm(forms.ModelForm):
    class Meta:
        model = Clients
        fields = "__all__"
        widgets = {
            "poblacio": autocomplete.ModelSelect2(
                url="poblacio-autocomplete",
                forward=["parroquia"],
                attrs={
                    "data-placeholder": "Selecciona una població...",
                    "data-minimum-input-length": 0,
                },
            ),
        }

    def clean(self):
        cleaned = super().clean()
        parroquia = cleaned.get("parroquia")
        poblacio = cleaned.get("poblacio")
        if parroquia and poblacio and poblacio.parroquia_id != parroquia.id:
            self.add_error("poblacio", "La població seleccionada no pertany a la parròquia indicada.")
        return cleaned
