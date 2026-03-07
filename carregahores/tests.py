from decimal import Decimal
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from carregahores.models import CarregaHores
from maestros.models import (
    Clients,
    DepartamentClient,
    Hores,
    Parroquia,
    PerfilUsuario,
    PersonaContactClient,
    Recurso,
    Tasca,
    TipusRecurso,
    Treball,
    Ubicacio,
)
from pressupostos.models import Pressupost, PressupostLinia
from projectes.models import Projecte


class MevesCarreguesIsolationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_a = User.objects.create_user(username="user_a", password="pass1234")
        cls.user_b = User.objects.create_user(username="user_b", password="pass1234")
        cls.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="pass1234"
        )

        cls.parroquia = Parroquia.objects.create(parroquia="Andorra la Vella")
        cls.ubicacio = Ubicacio.objects.create(ubicacio="Centre")
        cls.client_maestro = Clients.objects.create(
            nom_client="Client Test",
            telefon="+376123456",
        )
        cls.departament = DepartamentClient.objects.create(nom="Compres")
        cls.persona_contacte = PersonaContactClient.objects.create(
            client=cls.client_maestro,
            nom_contacte="Contacte Test",
            telefon="+376654321",
        )
        cls.projecte = Projecte.objects.create(
            nom="Projecte Test",
            client=cls.client_maestro,
            departament=cls.departament,
            persona_contacte=cls.persona_contacte,
            parroquia=cls.parroquia,
            ubicacio=cls.ubicacio,
        )
        cls.pressupost = Pressupost.objects.create(
            client=cls.client_maestro,
            projecte=cls.projecte,
            parroquia=cls.parroquia,
            ubicacio=cls.ubicacio,
            nom="P-001",
        )

        cls.tipus_recurs = TipusRecurso.objects.create(tipus="intern")
        cls.recurs = Recurso.objects.create(
            nom="Recurs Compartit",
            tipus_recurso=cls.tipus_recurs,
            preu_tancat=0,
            preu_hora=Decimal("25.00"),
        )
        PerfilUsuario.objects.filter(user=cls.user_a).update(recurso=cls.recurs)
        PerfilUsuario.objects.filter(user=cls.user_b).update(recurso=cls.recurs)

        cls.treball = Treball.objects.create(descripcio="Treball Test")
        cls.tasca = Tasca.objects.create(tasca="Tasca Test")
        cls.hora = Hores.objects.create(hores=Decimal("1.00"))

        cls.linia = PressupostLinia.objects.create(
            pressupost=cls.pressupost,
            treball=cls.treball,
            tasca=cls.tasca,
            quantitat=1,
            recurs=cls.recurs,
            preu_tancat=False,
            hora=cls.hora,
            increment_hores=Decimal("0.00"),
            hores_totals=Decimal("1.00"),
            cost_hores=Decimal("25.00"),
            cost_hores_totals=Decimal("25.00"),
            subtotal=Decimal("25.00"),
            benefici=Decimal("0.00"),
            total=Decimal("25.00"),
        )

        cls.carrega_a = CarregaHores.objects.create(
            usuari=cls.user_a,
            pressupost=cls.pressupost,
            linia=cls.linia,
            hores=Decimal("1.00"),
        )
        cls.carrega_b = CarregaHores.objects.create(
            usuari=cls.user_b,
            pressupost=cls.pressupost,
            linia=cls.linia,
            hores=Decimal("2.00"),
        )

    def test_meves_carregues_shows_only_current_user_records(self):
        self.client.force_login(self.user_a)
        response = self.client.get(reverse("carregahores:meves"))

        self.assertEqual(response.status_code, 200)
        carregues = response.context["carregues"]

        self.assertEqual(carregues.count(), 1)
        self.assertEqual(carregues.first().pk, self.carrega_a.pk)
        self.assertNotIn(self.carrega_b.pk, carregues.values_list("pk", flat=True))

    def test_owner_can_access_edit_within_24_hours(self):
        self.client.force_login(self.user_a)
        response = self.client.get(reverse("carregahores:editar", args=[self.carrega_a.pk]))
        self.assertEqual(response.status_code, 200)

    def test_non_owner_cannot_access_edit(self):
        self.client.force_login(self.user_b)
        response = self.client.get(reverse("carregahores:editar", args=[self.carrega_a.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("carregahores:meves"))

    def test_owner_cannot_delete_after_24_hours(self):
        self.carrega_a.creat = timezone.now() - timedelta(hours=25)
        self.carrega_a.save(update_fields=["creat"])

        self.client.force_login(self.user_a)
        response = self.client.post(reverse("carregahores:eliminar", args=[self.carrega_a.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("carregahores:meves"))
        self.assertTrue(CarregaHores.objects.filter(pk=self.carrega_a.pk).exists())

    def test_admin_can_delete_any_carrega(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("carregahores:eliminar", args=[self.carrega_b.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("carregahores:meves"))
        self.assertFalse(CarregaHores.objects.filter(pk=self.carrega_b.pk).exists())

    def test_login_required_for_carregahores_routes(self):
        urls = [
            reverse("carregahores:nova"),
            reverse("carregahores:meves"),
            reverse("carregahores:editar", args=[self.carrega_a.pk]),
            reverse("carregahores:ajax_lineas"),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/accounts/login/", response["Location"])

    def test_admin_views_redirect_non_admin_to_admin_login(self):
        self.client.force_login(self.user_a)
        urls = [
            reverse("carregahores:admin_totes"),
            reverse("carregahores:admin_stats"),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/admin/login/", response["Location"])

    def test_eliminar_get_returns_405(self):
        self.client.force_login(self.user_a)
        response = self.client.get(reverse("carregahores:eliminar", args=[self.carrega_a.pk]))
        self.assertEqual(response.status_code, 405)

    def test_ajax_lineas_post_returns_405(self):
        self.client.force_login(self.user_a)
        response = self.client.post(
            reverse("carregahores:ajax_lineas"),
            {"pressupost": self.pressupost.pk},
        )
        self.assertEqual(response.status_code, 405)
