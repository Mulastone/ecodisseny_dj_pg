from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from carregahores.models import CarregaHores
from maestros.models import (
    Clients,
    DepartamentClient,
    Desplacament,
    Hores,
    Parroquia,
    PersonaContactClient,
    Recurso,
    Tasca,
    TasquesTreball,
    TipusRecurso,
    Treball,
    Ubicacio,
)
from pressupostos.models import Pressupost, PressupostLinia
from projectes.models import Projecte


class PressupostosAjaxPermissionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="pass1234"
        )
        cls.user = User.objects.create_user(username="user", password="pass1234")

        cls.parroquia = Parroquia.objects.create(parroquia="Andorra la Vella")
        cls.ubicacio = Ubicacio.objects.create(ubicacio="Centre")
        cls.cliente = Clients.objects.create(
            nom_client="Client Test",
            telefon="+376123456",
        )
        cls.departament = DepartamentClient.objects.create(nom="Compres")
        cls.persona_contacte = PersonaContactClient.objects.create(
            client=cls.cliente,
            nom_contacte="Contacte Test",
            telefon="+376654321",
        )
        cls.projecte = Projecte.objects.create(
            nom="Projecte Test",
            client=cls.cliente,
            departament=cls.departament,
            persona_contacte=cls.persona_contacte,
            parroquia=cls.parroquia,
            ubicacio=cls.ubicacio,
        )

        cls.tasca = Tasca.objects.create(tasca="Tasca Test")
        cls.treball = Treball.objects.create(descripcio="Treball Test")
        TasquesTreball.objects.create(tasca=cls.tasca, treball=cls.treball)

        cls.tipus_recurs = TipusRecurso.objects.create(tipus="intern")
        Recurso.objects.create(
            nom="Recurs Reservat",
            tipus_recurso=cls.tipus_recurs,
            preu_tancat=0,
            preu_hora=Decimal("10.00"),
        )
        cls.recurs = Recurso.objects.create(
            nom="Recurs Test",
            tipus_recurso=cls.tipus_recurs,
            preu_tancat=0,
            preu_hora=Decimal("25.00"),
        )

        cls.desplacament = Desplacament.objects.create(
            parroquia=cls.parroquia,
            ubicacio=cls.ubicacio,
            tasca=cls.tasca,
            increment_hores=Decimal("1.50"),
        )

    def test_ajax_endpoints_redirect_for_non_admin(self):
        self.client.force_login(self.user)

        urls = [
            reverse("pressupostos:get_increment_hores")
            + f"?id_parroquia={self.parroquia.pk}&id_ubicacio={self.ubicacio.pk}&id_tasca={self.tasca.pk}",
            reverse("pressupostos:get_projectes_by_client", args=[self.cliente.pk]),
            reverse("pressupostos:get_tasques_by_treball", args=[self.treball.pk]),
            reverse("pressupostos:get_recurso", args=[self.recurs.pk]),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/admin/login/", response["Location"])

    def test_ajax_endpoints_work_for_admin(self):
        self.client.force_login(self.admin)

        increment_url = reverse("pressupostos:get_increment_hores") + (
            f"?id_parroquia={self.parroquia.pk}&id_ubicacio={self.ubicacio.pk}&id_tasca={self.tasca.pk}"
        )
        increment_response = self.client.get(increment_url)
        self.assertEqual(increment_response.status_code, 200)
        self.assertEqual(increment_response.json()["increment_hores"], 1.5)

        projectes_response = self.client.get(
            reverse("pressupostos:get_projectes_by_client", args=[self.cliente.pk])
        )
        self.assertEqual(projectes_response.status_code, 200)
        self.assertEqual(len(projectes_response.json()), 1)
        self.assertEqual(projectes_response.json()[0]["id"], self.projecte.pk)

        tasques_response = self.client.get(
            reverse("pressupostos:get_tasques_by_treball", args=[self.treball.pk])
        )
        self.assertEqual(tasques_response.status_code, 200)
        self.assertEqual(tasques_response.json()["tasques"][0]["id"], self.tasca.pk)

        recurso_response = self.client.get(
            reverse("pressupostos:get_recurso", args=[self.recurs.pk])
        )
        self.assertEqual(recurso_response.status_code, 200)
        self.assertEqual(recurso_response.json()["PreuHora"], "25.00")


class PressupostosDeleteAjaxTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username="admin_del", email="admin_del@example.com", password="pass1234"
        )
        cls.user = User.objects.create_user(username="user_del", password="pass1234")

        cls.parroquia = Parroquia.objects.create(parroquia="Escaldes")
        cls.ubicacio = Ubicacio.objects.create(ubicacio="Zona Test")
        cls.cliente = Clients.objects.create(
            nom_client="Client Delete Test",
            telefon="+376123457",
        )
        cls.departament = DepartamentClient.objects.create(nom="Operacions")
        cls.persona_contacte = PersonaContactClient.objects.create(
            client=cls.cliente,
            nom_contacte="Contacte Delete",
            telefon="+376654322",
        )
        cls.projecte = Projecte.objects.create(
            nom="Projecte Delete",
            client=cls.cliente,
            departament=cls.departament,
            persona_contacte=cls.persona_contacte,
            parroquia=cls.parroquia,
            ubicacio=cls.ubicacio,
        )

        cls.tasca = Tasca.objects.create(tasca="Tasca Delete")
        cls.treball = Treball.objects.create(descripcio="Treball Delete")
        TasquesTreball.objects.create(tasca=cls.tasca, treball=cls.treball)
        cls.tipus_recurs = TipusRecurso.objects.create(tipus="intern")
        cls.recurs = Recurso.objects.create(
            nom="Recurs Delete",
            tipus_recurso=cls.tipus_recurs,
            preu_tancat=0,
            preu_hora=Decimal("20.00"),
        )
        cls.hora = Hores.objects.create(hores=Decimal("1.00"))

        cls.pressupost_with_hours = Pressupost.objects.create(
            client=cls.cliente,
            projecte=cls.projecte,
            parroquia=cls.parroquia,
            ubicacio=cls.ubicacio,
            nom="P-WITH-HOURS",
        )
        cls.linia_with_hours = PressupostLinia.objects.create(
            pressupost=cls.pressupost_with_hours,
            treball=cls.treball,
            tasca=cls.tasca,
            quantitat=1,
            recurs=cls.recurs,
            preu_tancat=False,
            hora=cls.hora,
            increment_hores=Decimal("0.00"),
            hores_totals=Decimal("1.00"),
            cost_hores=Decimal("20.00"),
            cost_hores_totals=Decimal("20.00"),
            subtotal=Decimal("20.00"),
            benefici=Decimal("0.00"),
            total=Decimal("20.00"),
        )
        CarregaHores.objects.create(
            usuari=cls.user,
            pressupost=cls.pressupost_with_hours,
            linia=cls.linia_with_hours,
            hores=Decimal("1.00"),
        )

        cls.pressupost_without_hours = Pressupost.objects.create(
            client=cls.cliente,
            projecte=cls.projecte,
            parroquia=cls.parroquia,
            ubicacio=cls.ubicacio,
            nom="P-WITHOUT-HOURS",
        )

    def test_delete_ajax_rejects_non_admin(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("pressupostos:delete_ajax", args=[self.pressupost_without_hours.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_delete_ajax_blocks_pressupost_with_carregues(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("pressupostos:delete_ajax", args=[self.pressupost_with_hours.pk])
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertTrue(Pressupost.objects.filter(pk=self.pressupost_with_hours.pk).exists())

    def test_delete_ajax_deletes_pressupost_without_carregues(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("pressupostos:delete_ajax", args=[self.pressupost_without_hours.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertFalse(Pressupost.objects.filter(pk=self.pressupost_without_hours.pk).exists())

    def test_admin_views_require_authentication(self):
        urls = [
            reverse("pressupostos:list"),
            reverse("pressupostos:detall", args=[self.pressupost_with_hours.pk]),
            reverse("pressupostos:create"),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/admin/login/", response["Location"])

    def test_delete_requires_post_method(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("pressupostos:delete", args=[self.pressupost_with_hours.pk])
        )
        self.assertEqual(response.status_code, 405)

    def test_delete_version_ajax_requires_post_method(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("pressupostos:delete_version_ajax", args=[1]))
        self.assertEqual(response.status_code, 405)
