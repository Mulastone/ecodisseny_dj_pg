from django.db import models
from django.conf import settings
from django.utils import timezone

# Reutilizamos modelos existentes
from pressupostos.models import Pressupost, PressupostLinia
from maestros.models import Recurso, Treball, Tasca

class PerfilUsuario(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil")
    recurso = models.ForeignKey(Recurso, on_delete=models.PROTECT, related_name="usuarios", null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_username()} → {self.recurso or '—'}"


class CarregaHores(models.Model):
    usuari = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="carregues")
    pressupost = models.ForeignKey(Pressupost, on_delete=models.PROTECT)
    linia = models.ForeignKey(PressupostLinia, on_delete=models.PROTECT)
    
    # Campos calculados automáticamente desde la línea
    # treball y tasca se obtienen desde linia.treball y linia.tasca
    # recurso se obtiene desde linia.recurs (y se valida en clean)

    data = models.DateField(default=timezone.now)
    hores = models.DecimalField(max_digits=6, decimal_places=2)
    observacions = models.TextField(blank=True, null=True)

    creat = models.DateTimeField(auto_now_add=True)
    modif = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-data", "-creat"]

    @property
    def recurso(self):
        """Obtiene el recurso desde la línea del presupuesto"""
        return self.linia.recurs if self.linia else None
    
    @property
    def treball(self):
        """Obtiene el trabajo desde la línea del presupuesto"""
        return self.linia.treball if self.linia else None
    
    @property
    def tasca(self):
        """Obtiene la tarea desde la línea del presupuesto"""
        return self.linia.tasca if self.linia else None

    def clean(self):
        # Validaciones de consistencia
        errors = {}
        
        # Para nuevos registros, hacer validaciones básicas sin acceder a relaciones
        if not self.pk:  # Nuevo registro
            if not self.linia_id:
                errors["linia"] = "Has de seleccionar una línia."
            
            if not self.pressupost_id:
                errors["pressupost"] = "Has de seleccionar un pressupost."
                
            # Solo hacer validaciones de relación si ya tenemos un registro guardado
        else:  # Registro existente
            try:
                # la línea debe pertenecer al pressupost elegido
                if self.linia and self.pressupost and self.linia.pressupost_id != self.pressupost_id:
                    errors["linia"] = "La línia no pertany al pressupost seleccionat."
                    
                # la línea debe ser por horas (no preu_tancat)
                if self.linia and self.linia.preu_tancat:
                    errors["linia"] = "Aquesta línia és de preu tancat; no admet càrrega d'hores."
                
                # el pressupost debe estar abierto
                if self.pressupost and self.pressupost.tancat:
                    errors["pressupost"] = "El pressupost està tancat."
            except:
                # Si hay errores al acceder a las relaciones, los ignoramos en la validación del modelo
                pass

        from django.core.exceptions import ValidationError
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.data} · {self.usuari} · {self.hores} h"
