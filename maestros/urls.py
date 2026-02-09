from django.urls import path
from dal import autocomplete
from .models import PersonaContactClient, Poblacio


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
        
        # Obtener el ID del cliente desde forward
        client_id = self.forwarded.get('client', None)
        
        # Debug: imprimir en consola
        import sys
        print(f"[DEBUG PersonaContactAutocomplete] client_id recibido: {client_id}", file=sys.stderr)
        print(f"[DEBUG PersonaContactAutocomplete] forwarded completo: {self.forwarded}", file=sys.stderr)

        if client_id:
            qs = qs.filter(client_id=client_id)
            print(f"[DEBUG PersonaContactAutocomplete] Filtrando por client_id={client_id}, resultados: {qs.count()}", file=sys.stderr)

        if self.q:
            qs = qs.filter(nom_contacte__icontains=self.q)
            print(f"[DEBUG PersonaContactAutocomplete] Filtrando por búsqueda '{self.q}', resultados: {qs.count()}", file=sys.stderr)

        return qs.order_by("nom_contacte")


urlpatterns = [
    path("poblacio-autocomplete/", PoblacioAutocomplete.as_view(), name="poblacio-autocomplete"),
    path("autocomplete/persona-contacte/", PersonaContactAutocomplete.as_view(), name="autocomplete_persona_contacte"),
]
