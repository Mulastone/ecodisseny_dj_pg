from django.db import models
from maestros.models import (
    Clients, DepartamentClient, PersonaContactClient,
    Parroquia, Ubicacio, SafeSaveModel
)
from django.utils import timezone



class Projecte(SafeSaveModel):
    nom = models.CharField("Nom del Projecte", max_length=255)
    data_peticio = models.DateField("Data de Petició", default=timezone.now)
    client = models.ForeignKey(Clients, models.DO_NOTHING, verbose_name="Client")
    departament = models.ForeignKey(DepartamentClient, models.DO_NOTHING, verbose_name="Departament Client")
    persona_contacte = models.ForeignKey(PersonaContactClient, models.DO_NOTHING, verbose_name="Persona Contacte")
    parroquia = models.ForeignKey(Parroquia, models.DO_NOTHING, verbose_name="Parròquia")
    ubicacio = models.ForeignKey(Ubicacio, models.DO_NOTHING, verbose_name="Ubicació")
    observacions = models.CharField("Observacions", max_length=1200, blank=True, null=True)
    tancat = models.BooleanField("Tancat", default=False)

    class Meta:
        verbose_name = "Projecte"
        verbose_name_plural = "Projectes"

    def __str__(self):
        return self.nom
