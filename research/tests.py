from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Document, ExtractedPage, EvaluationCase, EvaluationRun
from .evaluation import _query_metrics


class AccountWorkflowTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_registration_creates_profile_and_logs_user_in(self):
        response = self.client.post(reverse("register"), {
            "username": "researcher",
            "email": "researcher@example.com",
            "password1": "SafePass!2026x",
            "password2": "SafePass!2026x",
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="researcher")
        self.assertTrue(user.is_authenticated)
        self.assertTrue(hasattr(user, "profile"))

    def test_login_and_logout(self):
        user = User.objects.create_user(
            username="reader", password="SafePass!2026x"
        )
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 200)
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)


class DocumentWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="owner", password="SafePass!2026x"
        )
        self.client.force_login(self.user)

    def test_txt_upload_extracts_text_and_creates_document_page(self):
        upload = SimpleUploadedFile(
            "research-notes.txt",
            "Evidence based research retrieval".encode("utf-8"),
            content_type="text/plain",
        )
        response = self.client.post(reverse("upload_document"), {
            "title": "Research notes",
            "description": "Test file",
            "file": upload,
        })
        self.assertEqual(response.status_code, 302)
        document = Document.objects.get(owner=self.user, title="Research notes")
        page = document.extracted_pages.get()
        self.assertEqual(page.page_number, None)
        self.assertIn("Evidence based research", page.text)
        self.assertEqual(document.extraction_status, Document.ExtractionStatus.COMPLETED)
        self.assertEqual(document.extracted_character_count, len(page.text))

    def test_pdf_upload_creates_page_record_and_reports_no_selectable_text(self):
        from pypdf import PdfWriter

        output = BytesIO()
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        writer.write(output)
        upload = SimpleUploadedFile(
            "blank-paper.pdf", output.getvalue(), content_type="application/pdf"
        )
        response = self.client.post(reverse("upload_document"), {
            "title": "Blank paper",
            "description": "",
            "file": upload,
        })
        self.assertEqual(response.status_code, 302)
        document = Document.objects.get(owner=self.user, title="Blank paper")
        extracted = document.extracted_pages.get()
        self.assertEqual(extracted.page_number, 1)
        self.assertEqual(document.extraction_status, Document.ExtractionStatus.NO_TEXT)

    def test_rejects_unsupported_file_type(self):
        upload = SimpleUploadedFile("script.exe", b"not allowed")
        response = self.client.post(reverse("upload_document"), {
            "title": "Invalid",
            "description": "",
            "file": upload,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Document.objects.filter(owner=self.user).exists())

    def test_document_is_private_from_another_user(self):
        other = User.objects.create_user(
            username="other", password="SafePass!2026x"
        )
        document = Document.objects.create(
            owner=self.user,
            title="Private notes",
            file=SimpleUploadedFile("private.txt", b"private text"),
        )
        self.client.force_login(other)
        response = self.client.get(
            reverse("document_detail", kwargs={"pk": document.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_dashboard_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)


class EvaluationMetricTests(TestCase):
    def test_metrics_calculated_for_relevant_results(self):
        class Page:
            def __init__(self, pk):
                self.pk = pk

        results = [{"page": Page(10)}, {"page": Page(20)}, {"page": Page(30)}]
        metrics = _query_metrics(results, {10, 30}, top_k=3)
        self.assertAlmostEqual(metrics["precision_at_k"], 2 / 3)
        self.assertAlmostEqual(metrics["recall_at_k"], 1.0)
        self.assertAlmostEqual(metrics["citation_accuracy"], 2 / 3)
        self.assertAlmostEqual(metrics["mrr"], 1.0)

    def test_empty_results_return_zero_quality_metrics(self):
        metrics = _query_metrics([], {10}, top_k=5)
        self.assertEqual(metrics["precision_at_k"], 0)
        self.assertEqual(metrics["recall_at_k"], 0)
        self.assertEqual(metrics["citation_accuracy"], 0)
        self.assertEqual(metrics["mrr"], 0)
