from django import forms
from django.contrib.auth.models import User
from maestros.models import Recurso
from pressupostos.models import Pressupost
from projectes.models import Projecte
from datetime import datetime, timedelta


class CarreguesFilterForm(forms.Form):
    # Filtro por usuario (solo para admin)
    usuari = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('first_name', 'last_name', 'username'),
        required=False,
        empty_label="--- Tots els usuaris ---",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Filtro por recurso
    recurs = forms.ModelChoiceField(
        queryset=Recurso.objects.all().order_by('nom'),
        required=False,
        empty_label="--- Tots els recursos ---",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Recurs"
    )
    
    # Filtro por proyecto
    projecte = forms.ModelChoiceField(
        queryset=Projecte.objects.all().order_by('nom'),
        required=False,
        empty_label="--- Tots els projectes ---",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Projecte"
    )
    
    # Filtro por presupuesto
    pressupost = forms.ModelChoiceField(
        queryset=Pressupost.objects.filter(tancat=False).order_by('nom'),
        required=False,
        empty_label="--- Tots els pressupostos ---",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Pressupost"
    )
    
    # Filtros de fecha
    data_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label="Data des de"
    )
    
    data_fins = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label="Data fins"
    )

    def __init__(self, *args, user=None, show_user_filter=True, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si no es admin, ocultar filtro de usuario Y filtro de recurso
        if not show_user_filter:
            del self.fields['usuari']
            # En vista personal, también ocultar el filtro de recurso (ya está filtrado automáticamente)
            del self.fields['recurs']
        else:
            # Solo para vista admin: Si hay usuario y no es admin, filtrar recursos por el usuario
            if user and not (user.is_superuser or user.is_staff):
                try:
                    # Obtener el recurso del usuario
                    user_resource = user.perfil.recurso if hasattr(user, 'perfil') and user.perfil else None
                    if user_resource:
                        # Solo mostrar el recurso del usuario
                        self.fields['recurs'].queryset = Recurso.objects.filter(id=user_resource.id)
                        self.fields['recurs'].initial = user_resource
                    else:
                        # Si no tiene recurso asignado, no mostrar ninguno
                        self.fields['recurs'].queryset = Recurso.objects.none()
                except:
                    # En caso de error, no mostrar recursos
                    self.fields['recurs'].queryset = Recurso.objects.none()
        
        # Valores por defecto útiles
        today = datetime.now().date()
        first_day_of_month = today.replace(day=1)
        
        # Sugerir rango del mes actual por defecto
        if not self.data:
            self.fields['data_desde'].initial = first_day_of_month
            self.fields['data_fins'].initial = today

    def get_queryset_filters(self):
        """Devuelve un diccionario con los filtros para aplicar al queryset"""
        filters = {}
        
        if self.is_valid():
            cleaned_data = self.cleaned_data
            
            if cleaned_data.get('usuari'):
                filters['usuari'] = cleaned_data['usuari']
            
            if cleaned_data.get('recurs'):
                filters['linia__recurs'] = cleaned_data['recurs']
            
            if cleaned_data.get('projecte'):
                filters['linia__pressupost__projecte'] = cleaned_data['projecte']
            
            if cleaned_data.get('pressupost'):
                filters['linia__pressupost'] = cleaned_data['pressupost']
            
            if cleaned_data.get('data_desde'):
                filters['data__gte'] = cleaned_data['data_desde']
            
            if cleaned_data.get('data_fins'):
                filters['data__lte'] = cleaned_data['data_fins']
        
        return filters