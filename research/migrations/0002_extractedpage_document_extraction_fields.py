from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("research", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="extraction_status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("completed", "Text extracted"),
                    ("no_text", "No selectable text"),
                ],
                default="pending",
                max_length=12,
            ),
        ),
        migrations.AddField(
            model_name="document",
            name="page_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="document",
            name="extracted_character_count",
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.CreateModel(
            name="ExtractedPage",
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
                ("page_number", models.PositiveIntegerField(blank=True, null=True)),
                ("text", models.TextField(blank=True)),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="extracted_pages",
                        to="research.document",
                    ),
                ),
            ],
            options={"ordering": ["page_number", "pk"]},
        ),
    ]
