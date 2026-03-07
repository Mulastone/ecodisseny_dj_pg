from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
    default_aplicar_increment_hores = models.BooleanField("Per defecte: aplicar increment hores", default=True)
    default_aplicar_cost_hores = models.BooleanField("Per defecte: aplicar cost hores", default=True)

    class Meta:
        verbose_name = "Pressupost"
        verbose_name_plural = "Pressupostos"
        permissions = (
            ("view_hores_report", "Pot veure l'informe d'hores previstes vs reals"),
        )

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
    aplicar_increment_hores = models.BooleanField(default=True)
    increment_hores = models.DecimalField(max_digits=5, decimal_places=2)
    hores_totals = models.DecimalField(max_digits=5, decimal_places=2)
    aplicar_cost_hores = models.BooleanField(default=True)
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
            try:
                # Usar el método de Django para eliminar archivos
                self.arxiu.delete(save=False)
            except (OSError, PermissionError) as e:
                # Si hay error de permisos, continuar con la eliminación del registro
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"No s'ha pogut eliminar l'arxiu PDF {self.arxiu.name}: {str(e)}")
        super().delete(*args, **kwargs)
