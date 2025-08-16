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
    recurso = models.ForeignKey(Recurso, on_delete=models.PROTECT)
    pressupost = models.ForeignKey(Pressupost, on_delete=models.PROTECT)
    linia = models.ForeignKey(PressupostLinia, on_delete=models.PROTECT)
    treball = models.ForeignKey(Treball, on_delete=models.PROTECT)
    tasca = models.ForeignKey(Tasca, on_delete=models.PROTECT)

    data = models.DateField(default=timezone.now)
    hores = models.DecimalField(max_digits=6, decimal_places=2)
    observacions = models.TextField(blank=True, null=True)

    creat = models.DateTimeField(auto_now_add=True)
    modif = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-data", "-creat"]

    def clean(self):
        # Validaciones de consistencia
        errors = {}
        # la línea debe pertenecer al pressupost elegido
        if self.linia and self.pressupost and self.linia.pressupost_id != self.pressupost.pk:
            errors["linia"] = "La línia no pertany al pressupost seleccionat."
        # la línea debe ser por horas (no preu_tancat)
        if self.linia and self.linia.preu_tancat:
            errors["linia"] = "Aquesta línia és de preu tancat; no admet càrrega d'hores."
        # el pressupost debe estar abierto
        if self.pressupost and self.pressupost.tancat:
            errors["pressupost"] = "El pressupost està tancat."
        # el recurso debe coincidir con la línea
        if self.linia and self.recurso and self.linia.recurs_id != self.recurso.pk:
            errors["recurso"] = "El recurs no coincideix amb el de la línia."
        # treball/tasca deben coincidir con la línea
        if self.linia:
            if self.treball_id != self.linia.treball_id:
                errors["treball"] = "El treball no coincideix amb la línia."
            if self.tasca_id != self.linia.tasca_id:
                errors["tasca"] = "La tasca no coincideix amb la línia."

        from django.core.exceptions import ValidationError
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.data} · {self.usuari} · {self.hores} h"
