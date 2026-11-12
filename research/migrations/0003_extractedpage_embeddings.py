from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("research", "0002_extractedpage_document_extraction_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="extractedpage",
            name="embedding_texts",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="extractedpage",
            name="embeddings",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="extractedpage",
            name="embedding_model",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
