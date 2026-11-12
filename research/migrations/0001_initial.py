# Generated for the Phase 1 research app.
import django.core.validators
import django.db.models.deletion
import research.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("institution", models.CharField(blank=True, max_length=150)),
                ("course", models.CharField(blank=True, max_length=100)),
                ("bio", models.TextField(blank=True, max_length=500)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Document",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("description", models.CharField(blank=True, max_length=500)),
                (
                    "file",
                    models.FileField(
                        upload_to=research.models.user_document_path,
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=("pdf", "txt")
                            )
                        ],
                    ),
                ),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("file_size", models.PositiveBigIntegerField(default=0)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-uploaded_at"]},
        ),
    ]
