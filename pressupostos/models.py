from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from maestros.models import (
    Clients, Treball, Tasca, Recurso, Hores,
    Parroquia, Ubicacio, SafeSaveModel
)
from projectes.models import Projecte


class Pressupost(SafeSaveModel):
    client = models.ForeignKey(Clients, models.DO_NOTHING)
    projecte = models.ForeignKey(Projecte, models.DO_NOTHING)
    parroquia = models.ForeignKey(Parroquia, models.DO_NOTHING)
    ubicacio = models.ForeignKey(Ubicacio, models.DO_NOTHING)
    nom = models.CharField("Nom del Pressupost", max_length=255, blank=True, null=True)
    data = models.DateField("Data del Pressupost", default=timezone.now)
    observacions = models.CharField("Observacions", max_length=600, blank=True, null=True)
    tancat = models.BooleanField("Tancat", default=False)

    class Meta:
        verbose_name = "Pressupost"
        verbose_name_plural = "Pressupostos"

    def __str__(self):
        return f"{self.nom} ({self.projecte})"


class PressupostLinia(SafeSaveModel):
    pressupost = models.ForeignKey(Pressupost, models.CASCADE, related_name="linies")
    treball = models.ForeignKey(Treball, models.DO_NOTHING)
    tasca = models.ForeignKey(Tasca, models.DO_NOTHING)
    quantitat = models.IntegerField()
    recurs = models.ForeignKey(Recurso, models.DO_NOTHING)
    preu_tancat = models.BooleanField(blank=True, null=True)
    cost_tancat = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    hora = models.ForeignKey(Hores, models.DO_NOTHING, blank=True, null=True)
    increment_hores = models.DecimalField(max_digits=5, decimal_places=2)
    hores_totals = models.DecimalField(max_digits=5, decimal_places=2)
    cost_hores = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    cost_hores_totals = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    benefici = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)

    class Meta:
        verbose_name = "Línia de Pressupost"
        verbose_name_plural = "Línies de Pressupost"

    def __str__(self):
        return f"Línia de {self.pressupost.nom or 'pressupost sense nom'}"


class PressupostPDFVersion(SafeSaveModel):
    pressupost = models.ForeignKey(Pressupost, on_delete=models.CASCADE, related_name="pdf_versions")
    version = models.PositiveIntegerField()
    arxiu = models.FileField(upload_to="media/pdfs_pressupostos/")
    generat_per = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    data_generat = models.DateTimeField(auto_now_add=True)
    html = models.TextField("Contingut HTML generat", blank=True, null=True)  # 👈 añadido

    class Meta:
        unique_together = ('pressupost', 'version')
        ordering = ['-version']
        verbose_name = "Versió PDF del Pressupost"
        verbose_name_plural = "Versions PDF dels Pressupostos"

    def __str__(self):
        return f"{self.pressupost} - Versió {self.version}"

