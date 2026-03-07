from django.urls import path
from dal import autocomplete
from .models import PersonaContactClient, Poblacio, Clients
from .views import poblacions_by_parroquia


class PoblacioAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Poblacio.objects.none()

        qs = Poblacio.objects.all()
        parroquia_id = self.forwarded.get('parroquia')

        if parroquia_id:
            qs = qs.filter(parroquia_id=parroquia_id)

        if self.q:
            qs = qs.filter(poblacio__icontains=self.q)

        return qs.order_by("poblacio")


class PersonaContactAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return PersonaContactClient.objects.none()

        qs = PersonaContactClient.objects.all()

        # El contacto depende del cliente seleccionado en el formulario.
        client_id = self.forwarded.get('client')
        if not client_id:
            return PersonaContactClient.objects.none()

        qs = qs.filter(client_id=client_id)

        if self.q:
            qs = qs.filter(nom_contacte__icontains=self.q)

        return qs.order_by("nom_contacte")


class ClientsAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Clients.objects.none()

        qs = Clients.objects.all()
        if self.q:
            qs = qs.filter(nom_client__icontains=self.q)

        return qs.order_by("nom_client")


urlpatterns = [
    path("poblacions-by-parroquia/", poblacions_by_parroquia, name="poblacions-by-parroquia"),
    path("autocomplete/clients/", ClientsAutocomplete.as_view(), name="autocomplete_clients"),
    path("poblacio-autocomplete/", PoblacioAutocomplete.as_view(), name="poblacio-autocomplete"),
    path("autocomplete/persona-contacte/", PersonaContactAutocomplete.as_view(), name="autocomplete_persona_contacte"),
]
