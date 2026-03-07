from dal import autocomplete
from django import forms
from .models import Projecte


class ProjectesForm(forms.ModelForm):
    class Meta:
        model = Projecte
        fields = '__all__'
        widgets = {
            'client': autocomplete.ModelSelect2(
                url='autocomplete_clients',
                attrs={
                    'data-placeholder': 'Selecciona un client...',
                    'data-minimum-input-length': 0,
                }
            ),
            'persona_contacte': autocomplete.ModelSelect2(
                url='autocomplete_persona_contacte',
                forward=['client'],
                attrs={
                    'data-placeholder': 'Selecciona un contacte...',
                    'data-minimum-input-length': 0,
                }
            )
        }

    def clean(self):
        cleaned = super().clean()
        client = cleaned.get("client")
        persona_contacte = cleaned.get("persona_contacte")

        if client and persona_contacte and persona_contacte.client_id != client.id:
            self.add_error(
                "persona_contacte",
                "La persona de contacte no pertany al client seleccionat."
            )

        return cleaned
