from django.db import models, IntegrityError
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError


class SafeSaveModel(models.Model):
    data_creacio = models.DateTimeField(auto_now_add=True)
    data_modificacio = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except IntegrityError as e:
            raise ValidationError(f"Error d'integritat: {str(e)}")


class Clients(SafeSaveModel):
    nom_client = models.CharField("Nom del Client", max_length=100)
    rao_social = models.CharField("Raó Social", max_length=100, blank=True, null=True)
    nrt = models.CharField("NRT", max_length=100, blank=True, null=True)
    parroquia = models.ForeignKey('Parroquia', models.DO_NOTHING, blank=True, null=True, verbose_name="Parròquia")
    poblacio = models.ForeignKey('Poblacio', models.DO_NOTHING, blank=True, null=True, verbose_name="Població")
    carrer = models.CharField("Carrer", max_length=100, blank=True, null=True)
    numero = models.CharField("Número", max_length=50, blank=True, null=True)
    escala = models.CharField("Escala", max_length=50, blank=True, null=True)
    pis = models.IntegerField("Pis", blank=True, null=True)
    porta = models.CharField("Porta", max_length=50, blank=True, null=True)
    telefon = PhoneNumberField("Telèfon")
    mail = models.EmailField("Correu electrònic", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.nom_client or "Client sense nom"


class Parroquia(SafeSaveModel):
    parroquia = models.CharField("Parròquia", max_length=100)

    class Meta:
        verbose_name = "Parròquia"
        verbose_name_plural = "Parròquies"

    def __str__(self):
        return self.parroquia


class Poblacio(SafeSaveModel):
    parroquia = models.ForeignKey(Parroquia, models.DO_NOTHING, verbose_name="Parròquia")
    poblacio = models.CharField("Població", max_length=100)
    codi_postal = models.CharField("Codi Postal", max_length=100)

    class Meta:
        verbose_name = "Població"
        verbose_name_plural = "Poblacions"

    def __str__(self):
        return self.poblacio


class TipusRecurso(SafeSaveModel):
    tipus = models.CharField("Tipus Recurs", max_length=100)

    class Meta:
        verbose_name = "Tipus de Recurs"
        verbose_name_plural = "Tipus de Recursos"

    def __str__(self):
        return self.tipus


class Recurso(SafeSaveModel):
    nom = models.CharField("Nom", max_length=100)
    tipus_recurso = models.ForeignKey(TipusRecurso, models.DO_NOTHING)
    preu_tancat = models.IntegerField("Preu Tancat")
    preu_hora = models.DecimalField("Preu Hora", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Recurs"
        verbose_name_plural = "Recursos"

    def __str__(self):
        return self.nom


class Tasca(SafeSaveModel):
    tasca = models.CharField(max_length=100)
    observacions = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Tasca"
        verbose_name_plural = "Tasques"

    def __str__(self):
        return self.tasca or "Tasca"


class Treball(SafeSaveModel):
    descripcio = models.CharField("Descripció", max_length=100)
    tasques = models.ManyToManyField(Tasca, through='TasquesTreball', related_name='treballs')

    class Meta:
        verbose_name = "Treball"
        verbose_name_plural = "Treballs"

    def __str__(self):
        return self.descripcio


class Ubicacio(SafeSaveModel):
    ubicacio = models.CharField("Ubicació", max_length=100)

    class Meta:
        verbose_name = "Ubicació"
        verbose_name_plural = "Ubicacions"

    def __str__(self):
        return self.ubicacio


class Desplacament(SafeSaveModel):
    parroquia = models.ForeignKey(Parroquia, models.DO_NOTHING)
    ubicacio = models.ForeignKey(Ubicacio, models.DO_NOTHING)
    tasca = models.ForeignKey(Tasca, models.DO_NOTHING)
    increment_hores = models.DecimalField("Increment Hores", max_digits=5, decimal_places=2)
    observacions = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Desplaçament"
        verbose_name_plural = "Desplaçaments"

    def __str__(self):
        return f"{self.parroquia} - {self.ubicacio} - {self.tasca}"


class Hores(SafeSaveModel):
    hores = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = "Hora"
        verbose_name_plural = "Hores"

    def __str__(self):
        return str(self.hores)


class TasquesTreball(SafeSaveModel):
    tasca = models.ForeignKey(Tasca, models.DO_NOTHING)
    treball = models.ForeignKey(Treball, models.DO_NOTHING)
    observacions = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        unique_together = ("tasca", "treball")
        verbose_name = "Treball - Tasca"
        verbose_name_plural = "Treballs - Tasques"

    def __str__(self):
        return f"{self.tasca} - {self.treball}"


class DepartamentClient(SafeSaveModel):
    nom = models.CharField("Departament Client", max_length=100)

    class Meta:
        verbose_name = "Departament Client"
        verbose_name_plural = "Departaments Clients"

    def __str__(self):
        return self.nom


class PersonaContactClient(SafeSaveModel):
    client = models.ForeignKey(Clients, models.DO_NOTHING, verbose_name="Client")
    nom_contacte = models.CharField("Contacte Client", max_length=100)
    telefon = PhoneNumberField("Telèfon", blank=True, null=True)

    class Meta:
        verbose_name = "Contacte Client"
        verbose_name_plural = "Contactes Client"

    def __str__(self):
        return self.nom_contacte
