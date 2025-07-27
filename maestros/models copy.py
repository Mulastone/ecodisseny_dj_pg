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
    id_client = models.AutoField(primary_key=True, verbose_name="ID")
    nom_client = models.CharField("Nom del Client", max_length=100)
    r_social = models.CharField("Raó Social", max_length=100, blank=True, null=True)
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
        db_table = 'clients'
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        app_label = 'maestros'

    def __str__(self):
        return self.nom_client or "Client sense nom"


class Parroquia(SafeSaveModel):
    id_parroquia = models.AutoField(primary_key=True)
    parroquia = models.CharField(max_length=100)

    class Meta:
        db_table = 'parroquia'
        verbose_name = "Parròquia"
        verbose_name_plural = "Parròquies"
        app_label = 'maestros'

    def __str__(self):
        return self.parroquia


class Poblacio(SafeSaveModel):
    id_poblacio = models.AutoField(primary_key=True)
    id_parroquia = models.ForeignKey(Parroquia, models.DO_NOTHING, verbose_name="Parròquia")
    poblacio = models.CharField(max_length=100)
    codi_postal = models.CharField(max_length=100)

    class Meta:
        db_table = 'poblacio'
        verbose_name = "Població"
        verbose_name_plural = "Poblacions"
        app_label = 'maestros'

    def __str__(self):
        return self.poblacio


class Recurso(SafeSaveModel):
    id_recurso = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    id_tipus_recurso = models.ForeignKey('Tipusrecurso', models.DO_NOTHING)
    preu_tancat = models.IntegerField()
    preu_hora = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'recurso'
        verbose_name = "Recurs"
        verbose_name_plural = "Recursos"
        app_label = 'maestros'

    def __str__(self):
        return self.name


class Tipusrecurso(SafeSaveModel):
    id_tipus_recurso = models.AutoField(primary_key=True)
    tipus = models.CharField("Tipus Recurs", max_length=100)

    class Meta:
        db_table = 'tipusrecurso'
        verbose_name = "Tipus de Recurs"
        verbose_name_plural = "Tipus de Recursos"
        app_label = 'maestros'

    def __str__(self):
        return self.tipus


class Tasca(SafeSaveModel):
    id_tasca = models.AutoField(primary_key=True)
    tasca = models.CharField(max_length=100)
    observacions = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'tasca'
        verbose_name = "Tasca"
        verbose_name_plural = "Tasques"
        app_label = 'maestros'

    def __str__(self):
        return self.tasca[:30]


class Treballs(SafeSaveModel):
    id_treball = models.AutoField(primary_key=True)
    descripcio = models.CharField(max_length=100)
    tasques = models.ManyToManyField('Tasca', through='TasquesTreball', related_name='treballs')

    class Meta:
        db_table = 'treballs'
        verbose_name = "Treball"
        verbose_name_plural = "Treballs"
        app_label = 'maestros'

    def __str__(self):
        return self.descripcio[:30]


class Ubicacio(SafeSaveModel):
    id_ubicacio = models.AutoField(primary_key=True)
    ubicacio = models.CharField("Ubicació", max_length=100)

    class Meta:
        db_table = 'ubicacio'
        verbose_name = "Ubicació"
        verbose_name_plural = "Ubicacions"
        app_label = 'maestros'

    def __str__(self):
        return self.ubicacio[:30]


class Desplacaments(SafeSaveModel):
    id_desplacament = models.AutoField(primary_key=True)
    id_parroquia = models.ForeignKey(Parroquia, models.DO_NOTHING, verbose_name="Parròquia")
    id_ubicacio = models.ForeignKey(Ubicacio, models.DO_NOTHING, verbose_name="Ubicació")
    id_tasca = models.ForeignKey(Tasca, models.DO_NOTHING, verbose_name="Tasca")
    increment_hores = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Increment Hores")
    observacions = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'desplacaments'
        verbose_name = "Desplaçament"
        verbose_name_plural = "Desplaçaments"
        app_label = 'maestros'

    def __str__(self):
        return f"Desplaçament {self.id_parroquia} - {self.id_tasca}"


class Hores(SafeSaveModel):
    id_hora = models.AutoField(primary_key=True)
    hores = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'hores'
        verbose_name = "Hora"
        verbose_name_plural = "Hores"
        app_label = 'maestros'

    def __str__(self):
        return str(self.hores)


class TasquesTreball(SafeSaveModel):
    id_tasca_treball = models.AutoField(primary_key=True)
    id_tasca = models.ForeignKey(Tasca, models.DO_NOTHING, verbose_name="Tasca")
    id_treball = models.ForeignKey(Treballs, models.DO_NOTHING, verbose_name="Treball")
    observacions = models.CharField("Observacions", max_length=300, blank=True, null=True)

    class Meta:
        db_table = 'tasques_treball'
        unique_together = (('id_tasca', 'id_treball'),)
        verbose_name = "Treball - Tasca"
        verbose_name_plural = "Treballs - Tasques"
        app_label = 'maestros'

    def __str__(self):
        return f"{self.id_tasca} - {self.id_treball}"


class DepartamentClient(SafeSaveModel):
    id_departament = models.AutoField(primary_key=True)
    nom = models.CharField("Departament Client", max_length=100)

    class Meta:
        db_table = 'departament_client'
        verbose_name = "Departament Client"
        verbose_name_plural = "Departaments Clients"
        app_label = 'maestros'

    def __str__(self):
        return self.nom


class PersonaContactClient(SafeSaveModel):
    id_persona_contact = models.AutoField(primary_key=True)
    id_client = models.ForeignKey(Clients, models.DO_NOTHING, verbose_name="Client")
    nom_contacte = models.CharField("Contacte Client", max_length=100)
    telefon = PhoneNumberField("Telèfon", blank=True, null=True)

    class Meta:
        db_table = 'persona_contact_client'
        verbose_name = "Contacte Client"
        verbose_name_plural = "Contactes Client"
        app_label = 'maestros'

    def __str__(self):
        return self.nom_contacte
