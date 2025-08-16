from django import forms
from django.forms import ModelForm, inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.forms.widgets import Select
from .models import Pressupost, PressupostLinia
from maestros.models import Hores


class HoresSelectWidget(Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        try:
            # Convert ModelChoiceIteratorValue to its actual value
            if hasattr(value, 'value'):
                actual_value = value.value
            else:
                actual_value = value
                
            if actual_value and str(actual_value).strip():
                hores_obj = Hores.objects.get(pk=actual_value)
                print(f"✅ DEBUG Widget - Value: {actual_value}, Hores obj: {hores_obj}, Hores value: {hores_obj.hores}")
                option['attrs']['data-hores'] = str(hores_obj.hores)
            else:
                print(f"⚠️ DEBUG Widget - Empty value: {actual_value}")
                option['attrs']['data-hores'] = "0"
        except Exception as e:
            print(f"❌ DEBUG Widget - Exception: {e}")
            option['attrs']['data-hores'] = "0"
        return option


class PressupostLiniaForm(ModelForm):
    class Meta:
        model = PressupostLinia
        exclude = ('data_creacio', 'data_modificacio')
        widgets = {
            'hora': HoresSelectWidget(),
            'preu_tancat': forms.CheckboxInput(),
            'increment_hores': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'hores_totals': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'cost_hores': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'cost_hores_totals': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'subtotal': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'total': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'benefici': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hora'].queryset = Hores.objects.all()
        self.fields['benefici'].initial = 10
        self.fields['quantitat'].initial = 1

    def clean(self):
        cleaned_data = super().clean()
        preu_tancat = cleaned_data.get("preu_tancat")
        hora = cleaned_data.get("hora")
        increment_hores = cleaned_data.get("increment_hores")
        hores_totals = cleaned_data.get("hores_totals")
        quantitat = cleaned_data.get("quantitat")
        cost_hores = cleaned_data.get("cost_hores")
        tasca = cleaned_data.get("tasca")
        recurs = cleaned_data.get("recurs")

        if quantitat is not None and quantitat < 0:
            self.add_error("quantitat", "La quantitat no pot ser negativa.")

        if not preu_tancat and cost_hores is not None and cost_hores < 0:
            self.add_error("cost_hores", "El cost per hora no pot ser negatiu.")

        if preu_tancat:
            if increment_hores not in (None, 0):
                self.add_error("increment_hores", "Ha de ser 0 si Preu Tancat està activat.")
            if hores_totals not in (None, 0):
                self.add_error("hores_totals", "Ha de ser 0 si Preu Tancat està activat.")
            if hora:
                self.add_error("hora", "Ha d'estar buit si Preu Tancat està activat.")
        else:
            if not hora:
                self.add_error("hora", "És obligatori si Preu Tancat no està activat.")

        if not tasca:
            self.add_error("tasca", "Cal seleccionar una tasca.")
        if not recurs:
            self.add_error("recurs", "Cal seleccionar un recurs.")

        return cleaned_data


class BasePressupostLiniaFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        has_linea = False

        for form in self.forms:
            if not form.is_valid():
                continue  # ⚠️ Importante: no procesar si el form aún no fue validado

            cleaned = getattr(form, "cleaned_data", {})
            if cleaned.get("DELETE"):
                continue

            if not cleaned.get("tasca") or not cleaned.get("recurs"):
                raise ValidationError("Totes les línies han de tenir una tasca i un recurs.")

            has_linea = True

        if not has_linea:
            raise ValidationError("El pressupost ha de tenir almenys una línia activa.")




PressupostLiniaFormSetCreate = inlineformset_factory(
    Pressupost,
    PressupostLinia,
    form=PressupostLiniaForm,
    formset=BasePressupostLiniaFormSet,
    extra=1,
    can_delete=True
)

PressupostLiniaFormSetEdit = inlineformset_factory(
    Pressupost,
    PressupostLinia,
    form=PressupostLiniaForm,
    formset=BasePressupostLiniaFormSet,
    extra=0,
    can_delete=True
)


class PressupostForm(ModelForm):
    data = forms.DateField(
        input_formats=['%d/%m/%Y'],
        widget=forms.TextInput(attrs={
            'class': 'form-control datepicker',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = Pressupost
        exclude = ('data_creacio', 'data_modificacio')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get("client")
        projecte = cleaned_data.get("projecte")
        if projecte and client and projecte.client != client:
            self.add_error("projecte", "El projecte no pertany al client seleccionat.")
        return cleaned_data
