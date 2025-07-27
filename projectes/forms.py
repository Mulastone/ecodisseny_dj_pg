from dal import autocomplete
from django import forms
from .models import Projecte


class ProjectesForm(forms.ModelForm):
    class Meta:
        model = Projecte
        fields = '__all__'
        widgets = {
            'persona_contacte': autocomplete.ModelSelect2(
                url='autocomplete_persona_contacte',
                forward=['client'],
                attrs={
                    'data-placeholder': 'Selecciona un contacte...',
                    'data-minimum-input-length': 0,
                }
            )
        }
