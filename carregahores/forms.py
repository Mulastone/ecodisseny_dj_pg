from django import forms
from .models import CarregaHores, PerfilUsuario
from pressupostos import models as pressupost_models

class CarregaHoresForm(forms.ModelForm):
    class Meta:
        model = CarregaHores
        fields = ["pressupost", "linia", "treball", "tasca", "hores", "data", "observacions", "recurso"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar pressupostos abiertos
        self.fields["pressupost"].queryset = pressupost_models.Pressupost.objects.filter(tancat=False)

        # Filtrar líneas por horas (no preu_tancat) y por pressupostos abiertos
        lineas = pressupost_models.PressupostLinia.objects.filter(
            pressupost__tancat=False,
            preu_tancat=False
        )

        # Si NO es admin, filtrar por el recurso del perfil
        if user and not user.is_superuser:
            perfil = getattr(user, "perfil", None)
            if not perfil or not perfil.recurso_id:
                # sin recurso asignado, que no vea nada
                lineas = lineas.none()
            else:
                lineas = lineas.filter(recurs_id=perfil.recurso_id)
                # recurso fijo para el form (no editable) = el del perfil
                self.fields["recurso"].initial = perfil.recurso
                self.fields["recurso"].disabled = True
        else:
            # admin puede elegir cualquier recurso
            pass

        self.fields["linia"].queryset = lineas

        # Si hay una instancia o datos iniciales, precargar treball/tasca
        linia = self.initial.get("linia") or self.data.get(self.add_prefix("linia")) or self.instance.linia_id
        if linia:
            try:
                l = pressupost_models.PressupostLinia.objects.get(pk=linia)
                self.fields["treball"].initial = l.treball_id
                self.fields["tasca"].initial = l.tasca_id
            except pressupost_models.PressupostLinia.DoesNotExist:
                pass

    def clean(self):
        cleaned = super().clean()
        user = self.initial.get("_user")  # truco para tener user en clean (lo pondremos en la vista)
        linia = cleaned.get("linia")
        recurso = cleaned.get("recurso")

        if user and not user.is_superuser:
            perfil = getattr(user, "perfil", None)
            if not perfil or not perfil.recurso_id:
                raise forms.ValidationError("No tens un recurs assignat.")
            if linia and linia.recurs_id != perfil.recurso_id:
                raise forms.ValidationError("No pots carregar hores en una línia d'un altre recurs.")
            # forzar recurso = del perfil
            cleaned["recurso"] = perfil.recurso

        # copiar treball/tasca desde la línea para consistencia
        if linia:
            cleaned["treball"] = linia.treball
            cleaned["tasca"] = linia.tasca

        return cleaned