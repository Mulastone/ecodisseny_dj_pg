from django import forms
from .models import CarregaHores, PerfilUsuario
from pressupostos import models as pressupost_models
from maestros.models import Hores

class HoresSelectWidget(forms.Select):
    """Widget para seleccionar horas con data-hores attribute"""
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
                option['attrs']['data-hores'] = str(hores_obj.hores)
            else:
                option['attrs']['data-hores'] = "0"
        except Exception:
            option['attrs']['data-hores'] = "0"
        return option

class CarregaHoresForm(forms.ModelForm):
    hores_seleccionades = forms.ModelChoiceField(
        queryset=Hores.objects.all(),
        widget=HoresSelectWidget(),
        label="Hores",
        help_text="Selecciona les hores treballades",
        required=True,
        empty_label="--- Selecciona les hores ---"
    )
    
    data = forms.DateField(
        input_formats=['%d/%m/%Y'],
        widget=forms.TextInput(attrs={
            'class': 'form-control datepicker',
            'autocomplete': 'off'
        })
    )
    
    class Meta:
        model = CarregaHores
        fields = ["pressupost", "linia", "hores_seleccionades", "hores", "data", "observacions"]
        widgets = {
            'observacions': forms.Textarea(attrs={'rows': 3}),
            'hores': forms.HiddenInput(),  # Campo oculto que se llena automáticamente
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer el campo hores no requerido aquí ya que lo llenamos automáticamente
        self.fields["hores"].required = False

        # Filtrar pressupostos abiertos y hacer el campo requerido
        self.fields["pressupost"].queryset = pressupost_models.Pressupost.objects.filter(tancat=False)
        self.fields["pressupost"].required = True
        self.fields["pressupost"].empty_label = "--- Selecciona un pressupost ---"

        # Filtrar líneas por horas (no preu_tancat) y por pressupostos abiertos
        lineas = pressupost_models.PressupostLinia.objects.filter(
            pressupost__tancat=False,
            preu_tancat=False
        )

        # Si NO es admin, filtrar por el recurso del perfil y configurar fecha
        if user and not user.is_superuser:
            perfil = getattr(user, "perfil", None)
            if not perfil or not perfil.recurso_id:
                # sin recurso asignado, que no vea nada
                lineas = lineas.none()
            else:
                lineas = lineas.filter(recurs_id=perfil.recurso_id)
            
            # Para usuarios normales: fecha de hoy por defecto y no editable
            from django.utils import timezone
            today = timezone.now().date()
            self.fields["data"].initial = today
            self.fields["data"].disabled = True
            self.fields["data"].widget.attrs.update({
                'readonly': True,
            })
            self.fields["data"].help_text = "La data és automàticament la d'avui per a usuaris normals"
        else:
            # Para admin: puede modificar la fecha pero con fecha de hoy por defecto
            from django.utils import timezone
            today = timezone.now().date()
            self.fields["data"].initial = today
            self.fields["data"].help_text = "Com a administrador, pots seleccionar qualsevol data"
        
        self.fields["linia"].queryset = lineas
        self.fields["linia"].required = True
        self.fields["linia"].empty_label = "--- Selecciona una línia ---"
        
        # Añadir información de recurso, treball y tasca al label de cada línea
        self.fields["linia"].label_from_instance = self._label_linia
        
        # Guardar el usuario para usar en clean()
        self._user = user

    def _label_linia(self, obj):
        """Genera un label descriptivo para cada línea"""
        return f"{obj.pressupost.nom} | {obj.recurs.nom} | {obj.treball.descripcio} | {obj.tasca.tasca}"

    def clean(self):
        cleaned = super().clean()
        user = self._user
        linia = cleaned.get("linia")
        hores_seleccionades = cleaned.get("hores_seleccionades")

        # CRÍTICO: Asegurar que las horas están establecidas SIEMPRE
        if hores_seleccionades:
            cleaned["hores"] = hores_seleccionades.hores
        
        # Verificar que hores no sea None o vacío después de asignarlo
        if not cleaned.get("hores"):
            raise forms.ValidationError("Has de seleccionar les hores treballades.")

        # Validar que el usuario tenga permiso para cargar en esta línea
        if user and not user.is_superuser:
            perfil = getattr(user, "perfil", None)
            if not perfil or not perfil.recurso_id:
                raise forms.ValidationError("No tens un recurs assignat.")
            if linia and linia.recurs_id != perfil.recurso_id:
                raise forms.ValidationError("No pots carregar hores en una línia d'un altre recurs.")
            
            # Para usuarios normales, forzar fecha de hoy
            from django.utils import timezone
            cleaned["data"] = timezone.now().date()

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # El pressupost se puede calcular automáticamente desde la línea
        if instance.linia:
            instance.pressupost = instance.linia.pressupost
        
        # Asegurar que las horas están establecidas
        hores_seleccionades = self.cleaned_data.get("hores_seleccionades")
        if hores_seleccionades and not instance.hores:
            instance.hores = hores_seleccionades.hores
        
        if commit:
            instance.save()
        return instance