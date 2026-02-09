from django import forms
from .models import CarregaHores
from maestros.models import PerfilUsuario, Clients
from pressupostos import models as pressupost_models
from projectes.models import Projecte
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


class ProjecteSelectWidget(forms.Select):
    """Widget para seleccionar proyectos con data-client attribute"""
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        try:
            # Convert ModelChoiceIteratorValue to its actual value
            if hasattr(value, 'value'):
                actual_value = value.value
            else:
                actual_value = value
                
            if actual_value and str(actual_value).strip():
                projecte_obj = Projecte.objects.get(pk=actual_value)
                client_id = projecte_obj.client.pk if projecte_obj.client else ''
                option['attrs']['data-client'] = str(client_id)
            else:
                option['attrs']['data-client'] = ""
        except Exception:
            option['attrs']['data-client'] = ""
        return option

class CarregaHoresForm(forms.ModelForm):
    # Campos de filtro (no se guardan en el modelo)
    client_filter = forms.ModelChoiceField(
        queryset=Clients.objects.all(),
        required=False,
        empty_label="--- Filtrar per client ---",
        label="Filtrar per Client",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_client_filter'})
    )
    
    projecte_filter = forms.ModelChoiceField(
        queryset=Projecte.objects.all(),
        required=False,
        empty_label="--- Filtrar per projecte ---",
        label="Filtrar per Projecte", 
        widget=ProjecteSelectWidget(attrs={'class': 'form-control', 'id': 'id_projecte_filter'})
    )
    
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
        fields = ["client_filter", "projecte_filter", "pressupost", "linia", "hores_seleccionades", "hores", "data", "observacions"]
        widgets = {
            'observacions': forms.Textarea(attrs={'rows': 3}),
            'hores': forms.HiddenInput(),  # Campo oculto que se llena automáticamente
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer el campo hores no requerido aquí ya que lo llenamos automáticamente
        self.fields["hores"].required = False

        # 🔐 SISTEMA DE PERMISOS BASADO EN ROLES
        is_admin = user and (user.is_superuser or user.is_staff)
        
        if is_admin:
            # 👑 ADMIN: Ve todos los presupuestos abiertos
            presupuestos_queryset = pressupost_models.Pressupost.objects.filter(tancat=False)
            self.fields["pressupost"].queryset = presupuestos_queryset
            self.fields["pressupost"].help_text = "🔓 Admin: Pots veure tots els pressupostos"
            
            # ADMIN: Ve todas las líneas de presupuestos abiertos
            lineas = pressupost_models.PressupostLinia.objects.filter(
                pressupost__tancat=False,
                preu_tancat=False
            )
            
            # Filtros para admin: todos los clientes y proyectos
            self.fields["client_filter"].queryset = Clients.objects.all()
            self.fields["projecte_filter"].queryset = Projecte.objects.all()
            
        else:
            # 👤 USUARIO NORMAL: Solo presupuestos donde está asignado
            perfil = getattr(user, "perfil", None)
            
            if not perfil or not perfil.recurso:
                # Sin recurso asignado, no ve nada
                presupuestos_queryset = pressupost_models.Pressupost.objects.none()
                self.fields["pressupost"].help_text = "❌ No tens cap recurs assignat. Contacta amb l'administrador."
                lineas = pressupost_models.PressupostLinia.objects.none()
                
                # Sin acceso a filtros
                self.fields["client_filter"].queryset = Clients.objects.none()
                self.fields["projecte_filter"].queryset = Projecte.objects.none()
                
            else:
                # Filtrar presupuestos donde tiene líneas asignadas
                presupuestos_asignados = pressupost_models.Pressupost.objects.filter(
                    tancat=False,
                    linies__recurs=perfil.recurso
                ).distinct()
                
                presupuestos_queryset = presupuestos_asignados
                self.fields["pressupost"].help_text = f"🎯 Recurs: {perfil.recurso.nom} - Només pressupostos assignats"
                
                # Solo líneas del usuario en presupuestos abiertos
                lineas = pressupost_models.PressupostLinia.objects.filter(
                    pressupost__tancat=False,
                    preu_tancat=False,
                    recurs=perfil.recurso
                )
                
                # Filtros: solo clientes y proyectos de presupuestos asignados
                clientes_asignados = Clients.objects.filter(
                    pressupost__in=presupuestos_asignados
                ).distinct()
                
                proyectos_asignados = Projecte.objects.filter(
                    pressupost__in=presupuestos_asignados
                ).distinct()
                
                self.fields["client_filter"].queryset = clientes_asignados
                self.fields["projecte_filter"].queryset = proyectos_asignados

        # Configurar campo pressupost
        self.fields["pressupost"].queryset = presupuestos_queryset
        self.fields["pressupost"].required = True
        self.fields["pressupost"].empty_label = "--- Selecciona un pressupost ---"
        self.fields["pressupost"].widget.attrs.update({
            'class': 'form-control',
            'id': 'id_pressupost',
            'data-client': '',  # Se llenará con JavaScript
            'data-projecte': ''  # Se llenará con JavaScript
        })

        # Configurar campo linia
        self.fields["linia"].queryset = lineas
        self.fields["linia"].required = True
        self.fields["linia"].empty_label = "--- Primer selecciona un pressupost ---"

        # Configurar fecha según el tipo de usuario
        if not is_admin:
            # Para usuarios normales: fecha de hoy por defecto
            from django.utils import timezone
            today = timezone.now().date()
            if 'data' not in self.initial:
                self.initial['data'] = today.strftime('%d/%m/%Y')
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

        # Remover campos de filtro del cleaned_data ya que no son parte del modelo
        cleaned.pop("client_filter", None)
        cleaned.pop("projecte_filter", None)

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


class EstadistiquesFilterForm(forms.Form):
    """Formulari per filtrar les estadístiques"""
    from datetime import datetime
    from maestros.models import Recurso
    
    # Filtros de fecha
    any = forms.ChoiceField(
        label="Any",
        required=False,
        choices=[('', 'Tots els anys')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    mes = forms.ChoiceField(
        label="Mes",
        required=False,
        choices=[
            ('', 'Tots els mesos'),
            ('1', 'Gener'), ('2', 'Febrer'), ('3', 'Març'),
            ('4', 'Abril'), ('5', 'Maig'), ('6', 'Juny'),
            ('7', 'Juliol'), ('8', 'Agost'), ('9', 'Setembre'),
            ('10', 'Octubre'), ('11', 'Novembre'), ('12', 'Desembre'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Filtros de relaciones
    client = forms.ModelChoiceField(
        label="Client",
        queryset=Clients.objects.all().order_by('nom_client'),
        required=False,
        empty_label="Tots els clients",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    projecte = forms.ModelChoiceField(
        label="Projecte",
        queryset=Projecte.objects.all().order_by('nom'),
        required=False,
        empty_label="Tots els projectes",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    pressupost = forms.ModelChoiceField(
        label="Pressupost",
        queryset=pressupost_models.Pressupost.objects.all().order_by('-data'),
        required=False,
        empty_label="Tots els pressupostos",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    recurs = forms.ModelChoiceField(
        label="Recurs",
        queryset=Recurso.objects.all().order_by('nom'),
        required=False,
        empty_label="Tots els recursos",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    usuari = forms.ModelChoiceField(
        label="Usuari",
        queryset=PerfilUsuario.objects.select_related('user').all(),
        required=False,
        empty_label="Tots els usuaris",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Generar opciones de años dinámicamente
        from django.db.models import Min, Max
        from datetime import datetime
        
        years_range = CarregaHores.objects.aggregate(
            min_year=Min('data__year'),
            max_year=Max('data__year')
        )
        
        if years_range['min_year'] and years_range['max_year']:
            year_choices = [('', 'Tots els anys')]
            for year in range(years_range['max_year'], years_range['min_year'] - 1, -1):
                year_choices.append((str(year), str(year)))
            self.fields['any'].choices = year_choices
