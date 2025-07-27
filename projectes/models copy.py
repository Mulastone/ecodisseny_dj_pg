from django.db import models
from django.utils import timezone
from maestros.models import (
    Clients, DepartamentClient, PersonaContactClient,
    Parroquia, Ubicacio, SafeSaveModel
)


class Projectes(SafeSaveModel):
    id_projecte = models.AutoField(primary_key=True)
    nom_projecte = models.CharField(max_length=255, blank=False, null=False)
    data_peticio = models.DateField(default=timezone.now, blank=False, null=False)
    id_client = models.ForeignKey(Clients, models.DO_NOTHING, verbose_name="Client")
    id_departament = models.ForeignKey(DepartamentClient, models.DO_NOTHING, verbose_name="Departament Client")
    id_persona_contact = models.ForeignKey(PersonaContactClient, models.DO_NOTHING, verbose_name="Persona Contacte")
    id_parroquia = models.ForeignKey(Parroquia, models.DO_NOTHING, verbose_name="Parròquia")
    id_ubicacio = models.ForeignKey(Ubicacio, models.DO_NOTHING, verbose_name="Ubicació")
    observacions = models.CharField(max_length=1200, blank=True, null=True)
    tancat = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'projectes'
        verbose_name = "Projecte"
        verbose_name_plural = "Projectes"

    def __str__(self):
        return self.nom_projecte
