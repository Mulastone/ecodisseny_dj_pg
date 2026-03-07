from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from documentacion.models import (
    CategoriaDocumentacion,
    DocumentoMarkdown,
    FeedbackDocumentacion,
    HistorialAcceso,
)


class AnalyticsDocumentacionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff_user = User.objects.create_user(
            username="staff_user",
            password="pass1234",
            is_staff=True,
        )
        cls.normal_user = User.objects.create_user(
            username="normal_user",
            password="pass1234",
        )

        cls.categoria = CategoriaDocumentacion.objects.create(
            nombre="General",
            slug="general",
            tipo="general",
            activa=True,
        )
        cls.documento = DocumentoMarkdown.objects.create(
            titulo="Doc Test",
            slug="doc-test",
            categoria=cls.categoria,
            archivo_markdown="README.md",
            publicado=True,
        )

        HistorialAcceso.objects.create(
            documento=cls.documento,
            usuario=cls.staff_user,
            ip_address="127.0.0.1",
            user_agent="test-agent",
        )
        FeedbackDocumentacion.objects.create(
            documento=cls.documento,
            usuario=cls.staff_user,
            tipo="util",
            comentario="ok",
            procesado=False,
        )

    def test_analytics_requires_staff(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(reverse("documentacion:analytics"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("documentacion:index"))

    def test_analytics_renders_expected_context_for_staff(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("documentacion:analytics"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("documentos_populares", response.context)
        self.assertIn("feedback_reciente", response.context)
        self.assertIn("stats_categorias", response.context)

        documentos_populares = list(response.context["documentos_populares"])
        self.assertGreaterEqual(len(documentos_populares), 1)
        self.assertEqual(documentos_populares[0].pk, self.documento.pk)
        self.assertEqual(documentos_populares[0].visitas, 1)


class FeedbackDocumentacionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="feedback_user",
            password="pass1234",
        )
        categoria = CategoriaDocumentacion.objects.create(
            nombre="General Feedback",
            slug="general-feedback",
            tipo="general",
            activa=True,
        )
        cls.documento = DocumentoMarkdown.objects.create(
            titulo="Doc Feedback",
            slug="doc-feedback",
            categoria=categoria,
            archivo_markdown="README.md",
            publicado=True,
        )

    def test_feedback_create_and_update(self):
        self.client.force_login(self.user)
        url = reverse("documentacion:feedback", args=[self.documento.pk])

        response_create = self.client.post(url, {"tipo": "util", "comentario": "ok"})
        self.assertEqual(response_create.status_code, 200)
        self.assertTrue(response_create.json()["success"])
        self.assertEqual(FeedbackDocumentacion.objects.count(), 1)

        response_update = self.client.post(
            url, {"tipo": "no_util", "comentario": "canviar"}
        )
        self.assertEqual(response_update.status_code, 200)
        self.assertTrue(response_update.json()["success"])
        self.assertEqual(FeedbackDocumentacion.objects.count(), 1)
        feedback = FeedbackDocumentacion.objects.get(documento=self.documento, usuario=self.user)
        self.assertEqual(feedback.tipo, "no_util")

    def test_feedback_rejects_invalid_type(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("documentacion:feedback", args=[self.documento.pk]),
            {"tipo": "mejoras", "comentario": "no valido"},
        )
        self.assertEqual(response.status_code, 400)


class DocumentacionAccessControlTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_with_group = User.objects.create_user(
            username="with_group",
            password="pass1234",
        )
        cls.user_without_group = User.objects.create_user(
            username="without_group",
            password="pass1234",
        )
        cls.restricted_group = Group.objects.create(name="DocsPrivats")

        cls.restricted_category = CategoriaDocumentacion.objects.create(
            nombre="Privada",
            slug="privada",
            tipo="admin",
            activa=True,
        )
        cls.restricted_category.grupos_permitidos.add(cls.restricted_group)

        cls.restricted_document = DocumentoMarkdown.objects.create(
            titulo="Doc Privat",
            slug="doc-privat",
            categoria=cls.restricted_category,
            archivo_markdown="README.md",
            autor=cls.user_with_group,
            publicado=True,
        )

        cls.user_with_group.groups.add(cls.restricted_group)

    def test_user_outside_group_cannot_access_restricted_category(self):
        self.client.force_login(self.user_without_group)
        response = self.client.get(
            reverse("documentacion:categoria", args=[self.restricted_category.slug])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("documentacion:index"))

    def test_user_outside_group_cannot_access_restricted_document(self):
        self.client.force_login(self.user_without_group)
        response = self.client.get(
            reverse(
                "documentacion:documento",
                args=[self.restricted_category.slug, self.restricted_document.slug],
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("documentacion:categoria", args=[self.restricted_category.slug]),
        )

    def test_user_with_group_can_access_restricted_category_and_document(self):
        self.client.force_login(self.user_with_group)

        category_response = self.client.get(
            reverse("documentacion:categoria", args=[self.restricted_category.slug])
        )
        self.assertEqual(category_response.status_code, 200)

        doc_response = self.client.get(
            reverse(
                "documentacion:documento",
                args=[self.restricted_category.slug, self.restricted_document.slug],
            )
        )
        self.assertEqual(doc_response.status_code, 200)


class DocumentacionSmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="doc_smoke", password="pass1234")
        categoria = CategoriaDocumentacion.objects.create(
            nombre="General Smoke",
            slug="general-smoke",
            tipo="general",
            activa=True,
        )
        cls.documento = DocumentoMarkdown.objects.create(
            titulo="Doc Smoke",
            slug="doc-smoke",
            categoria=categoria,
            archivo_markdown="README.md",
            publicado=True,
        )

    def test_login_required_for_documentacion_routes(self):
        urls = [
            reverse("documentacion:index"),
            reverse("documentacion:busqueda"),
            reverse("documentacion:analytics"),
            reverse("documentacion:categoria", args=["general-smoke"]),
            reverse("documentacion:documento", args=["general-smoke", "doc-smoke"]),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/accounts/login/", response["Location"])

    def test_feedback_get_returns_405(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("documentacion:feedback", args=[self.documento.pk]))
        self.assertEqual(response.status_code, 405)
