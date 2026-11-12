from pathlib import Path
from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator

def user_document_path(instance, filename):
    # Keep each user's uploads in a separate folder.
    safe_name = Path(filename).name
    return f"user_{instance.owner_id}/documents/{safe_name}"

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    institution = models.CharField(max_length=150, blank=True)
    course = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"Profile: {self.user.username}"

class Document(models.Model):
    class ExtractionStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Text extracted"
        NO_TEXT = "no_text", "No selectable text"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="documents"
    )
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    file = models.FileField(
        upload_to=user_document_path,
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "txt"])],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.PositiveBigIntegerField(default=0)
    extraction_status = models.CharField(
        max_length=12,
        choices=ExtractionStatus.choices,
        default=ExtractionStatus.PENDING,
    )
    page_count = models.PositiveIntegerField(default=0)
    extracted_character_count = models.PositiveBigIntegerField(default=0)

    class Meta:
        ordering = ["-uploaded_at"]

    def save(self, *args, **kwargs):
        if self.file:
            try:
                self.file_size = self.file.size
            except (OSError, ValueError):
                pass
        super().save(*args, **kwargs)

    @property
    def filename(self):
        return Path(self.file.name).name

    def __str__(self):
        return self.title


class ExtractedPage(models.Model):
    """Text extracted from one PDF page or one uploaded TXT document."""

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="extracted_pages"
    )
    # TXT files have no physical page number, so their value is NULL.
    page_number = models.PositiveIntegerField(null=True, blank=True)
    text = models.TextField(blank=True)
    embedding_texts = models.JSONField(default=list, blank=True)
    embeddings = models.JSONField(default=list, blank=True)
    embedding_model = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ["page_number", "pk"]

    def __str__(self):
        label = f"page {self.page_number}" if self.page_number else "text file"
        return f"{self.document.title} — {label}"


class EvaluationCase(models.Model):
    """A research question and its manually labeled relevant source pages."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="evaluation_cases",
    )
    question = models.CharField(max_length=500)
    relevant_pages = models.ManyToManyField(
        ExtractedPage,
        blank=True,
        related_name="evaluation_cases",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]

    def __str__(self):
        return self.question


class EvaluationRun(models.Model):
    """Saved metrics and findings for one labeled retrieval comparison."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="evaluation_runs",
    )
    top_k = models.PositiveSmallIntegerField(default=5)
    question_count = models.PositiveIntegerField(default=0)
    report = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]

    def __str__(self):
        return f"Evaluation on {self.created_at:%Y-%m-%d %H:%M}"
