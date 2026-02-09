from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
import os

from maestros.models import (
    Clients, Treball, Tasca, Recurso, Hores,
    Parroquia, Ubicacio, SafeSaveModel
)
from projectes.models import Projecte


class Pressupost(SafeSaveModel):
    client = models.ForeignKey(Clients, models.PROTECT)
    projecte = models.ForeignKey(Projecte, models.PROTECT)
    parroquia = models.ForeignKey(Parroquia, models.PROTECT)
    ubicacio = models.ForeignKey(Ubicacio, models.PROTECT)
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
    treball = models.ForeignKey(Treball, models.PROTECT)
    tasca = models.ForeignKey(Tasca, models.PROTECT)
    quantitat = models.IntegerField()
    recurs = models.ForeignKey(Recurso, models.PROTECT)
    preu_tancat = models.BooleanField(blank=True, null=True)
    cost_tancat = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    hora = models.ForeignKey(Hores, models.PROTECT, blank=True, null=True)
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
    arxiu = models.FileField(upload_to="pdfs_pressupostos/")
    generat_per = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    data_generat = models.DateTimeField(auto_now_add=True)
    html = models.TextField("Contingut HTML generat", blank=True, null=True)

    class Meta:
        unique_together = ('pressupost', 'version')
        ordering = ['-version']
        verbose_name = "Versió PDF del Pressupost"
        verbose_name_plural = "Versions PDF dels Pressupostos"

    def __str__(self):
        return f"{self.pressupost} - Versió {self.version}"
    
    def delete(self, *args, **kwargs):
        """Elimina el archivo físico antes de eliminar el registro"""
        if self.arxiu:
            if os.path.isfile(self.arxiu.path):
                os.remove(self.arxiu.path)
        super().delete(*args, **kwargs)


@receiver(pre_delete, sender=PressupostPDFVersion)
def eliminar_arxiu_pdf(sender, instance, **kwargs):
    """Señal para eliminar el archivo PDF cuando se elimina el registro"""
    if instance.arxiu:
        if os.path.isfile(instance.arxiu.path):
            os.remove(instance.arxiu.path)

