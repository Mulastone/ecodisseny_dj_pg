from django.db import models
from django.utils import timezone
from maestros.models import (
    Clients, Treballs, Tasca, Recurso, Hores,
    Parroquia, Ubicacio, SafeSaveModel
)
from projectes.models import Projectes
from django.contrib.auth.models import User


class Pressupostos(SafeSaveModel):
    id_pressupost = models.AutoField(primary_key=True)
    id_client = models.ForeignKey(Clients, models.DO_NOTHING)
    id_projecte = models.ForeignKey(Projectes, models.DO_NOTHING)
    id_parroquia = models.ForeignKey(Parroquia, models.DO_NOTHING)
    id_ubicacio = models.ForeignKey(Ubicacio, models.DO_NOTHING)
    nom_pressupost = models.CharField(max_length=255, blank=True, null=True)
    data_pressupost = models.DateField(default=timezone.now)
    observacions = models.CharField(max_length=600, blank=True, null=True)
    tancat = models.BooleanField(default=False)

    class Meta:
        db_table = 'pressupostos'
        verbose_name = "Pressupost"
        verbose_name_plural = "Pressupostos"
        app_label = 'pressupostos'

    def __str__(self):
        return f"{self.nom_pressupost} ({self.id_projecte})"


class PressupostosLineas(SafeSaveModel):
    id_pressupost_linea = models.AutoField(primary_key=True)
    id_pressupost = models.ForeignKey(Pressupostos, models.DO_NOTHING)
    id_treball = models.ForeignKey(Treballs, models.DO_NOTHING)
    id_tasca = models.ForeignKey(Tasca, models.DO_NOTHING)
    quantitat = models.IntegerField()
    id_recurso = models.ForeignKey(Recurso, models.DO_NOTHING)
    preu_tancat = models.BooleanField(blank=True, null=True)
    cost_tancat = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    id_hora = models.ForeignKey(Hores, models.DO_NOTHING, blank=True, null=True)
    increment_hores = models.DecimalField(max_digits=5, decimal_places=2)
    hores_totals = models.DecimalField(max_digits=5, decimal_places=2)
    cost_hores = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    cost_hores_totals = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    subtotal_linea = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    benefici_linea = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    total_linea = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)

    class Meta:
        db_table = 'pressupostos_lineas'
        verbose_name = "Línia de Pressupost"
        verbose_name_plural = "Línies de Pressupost"
        app_label = 'pressupostos'

    def __str__(self):
        return f"Línia {self.id_pressupost_linea} - Pressupost {self.id_pressupost_id}"


class PressupostPDFVersion(SafeSaveModel):
    pressupost = models.ForeignKey(Pressupostos, on_delete=models.CASCADE, related_name="pdf_versions")
    version = models.PositiveIntegerField()
    archivo = models.FileField(upload_to="media/pdfs_pressupostos/")
    generat_per = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    data_generat = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('pressupost', 'version')
        ordering = ['-version']

    def __str__(self):
        return f"Pressupost #{self.pressupost.id_pressupost} - Versió {self.version}"
