from django.contrib import admin
from .models import Profile, Document, ExtractedPage, EvaluationCase, EvaluationRun

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "institution", "course")

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "owner",
        "uploaded_at",
        "file_size",
        "extraction_status",
        "page_count",
    )
    list_filter = ("uploaded_at", "extraction_status")
    search_fields = ("title", "description", "owner__username")


@admin.register(ExtractedPage)
class ExtractedPageAdmin(admin.ModelAdmin):
    list_display = ("document", "page_number", "embedding_model")
    search_fields = ("document__title", "text")


@admin.register(EvaluationCase)
class EvaluationCaseAdmin(admin.ModelAdmin):
    list_display = ("question", "owner", "created_at")
    search_fields = ("question", "owner__username")


@admin.register(EvaluationRun)
class EvaluationRunAdmin(admin.ModelAdmin):
    list_display = ("owner", "top_k", "question_count", "created_at")
    readonly_fields = ("report",)
