from pathlib import Path
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Document, ExtractedPage, EvaluationCase

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_SEARCH_TERMS = 10

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["institution", "course", "bio"]
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "description", "file"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Research Paper on NLP"}),
            "description": forms.TextInput(attrs={"placeholder": "Optional short description"}),
        }

    def clean_file(self):
        uploaded = self.cleaned_data["file"]
        suffix = Path(uploaded.name).suffix.lower()
        if suffix not in {".pdf", ".txt"}:
            raise forms.ValidationError("Only PDF and TXT files are allowed.")
        if uploaded.size > MAX_FILE_SIZE:
            raise forms.ValidationError("File is too large. Maximum size is 10 MB.")
        # Basic signature check for PDFs. Text files are accepted as uploaded text.
        if suffix == ".pdf":
            header = uploaded.read(5)
            uploaded.seek(0)
            if header != b"%PDF-":
                raise forms.ValidationError("This does not appear to be a valid PDF file.")
        return uploaded


class DocumentSearchForm(forms.Form):
    RETRIEVAL_MODES = [
        ("keyword", "Keyword"),
        ("semantic", "Semantic"),
        ("hybrid", "Hybrid (recommended)"),
    ]

    q = forms.CharField(
        max_length=200,
        label="Question or keywords",
        widget=forms.SearchInput(attrs={"placeholder": "Ask about your documents"}),
    )
    mode = forms.ChoiceField(
        choices=RETRIEVAL_MODES,
        required=False,
        label="Retrieval method",
    )

    def clean_q(self):
        query = self.cleaned_data["q"].strip()
        terms = re.findall(r"\w+", query, flags=re.UNICODE)
        if not terms:
            raise forms.ValidationError("Enter at least one search keyword.")
        if len(terms) > MAX_SEARCH_TERMS:
            raise forms.ValidationError(
                f"Use no more than {MAX_SEARCH_TERMS} keywords in one search."
            )
        return query

    def clean_mode(self):
        return self.cleaned_data.get("mode") or "hybrid"


class EvaluationCaseForm(forms.ModelForm):
    relevant_pages = forms.ModelMultipleChoiceField(
        queryset=ExtractedPage.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "page-choices"}),
        label="Relevant source pages",
        help_text="Select every page that contains evidence relevant to this question.",
    )

    class Meta:
        model = EvaluationCase
        fields = ["question", "relevant_pages"]
        widgets = {"question": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["relevant_pages"].queryset = (
                ExtractedPage.objects
                .filter(document__owner=user)
                .exclude(text="")
                .select_related("document")
                .order_by("document__title", "page_number", "pk")
            )


class EvaluationRunForm(forms.Form):
    top_k = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=5,
        label="Results to evaluate per question (k)",
        widget=forms.NumberInput(attrs={"min": 1, "max": 10}),
    )
