from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .forms import (
    RegistrationForm,
    ProfileForm,
    DocumentUploadForm,
    DocumentSearchForm,
    EvaluationCaseForm,
    EvaluationRunForm,
)
from .models import Document, ExtractedPage, EvaluationCase, EvaluationRun
from .evaluation import build_evaluation_report
from .services import DocumentExtractionError, extract_uploaded_text
from .retrieval import retrieve_pages
from .semantic_search import SemanticSearchUnavailable

def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "research/home.html")

def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account has been created.")
        return redirect("dashboard")
    return render(request, "research/register.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, "Welcome back.")
        next_url = request.POST.get("next") or request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect("dashboard")
    return render(request, "research/login.html", {"form": form})

@login_required
def logout_view(request):
    if request.method != "POST":
        return redirect("dashboard")
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")

@login_required
def dashboard(request):
    query = request.GET.get("q", "").strip()
    documents = Document.objects.filter(owner=request.user)
    if query:
        documents = documents.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(file__icontains=query)
        )
    return render(request, "research/dashboard.html", {
        "documents": documents,
        "query": query,
        "total_documents": Document.objects.filter(owner=request.user).count(),
    })

@login_required
def search_documents(request):
    form_data = request.GET.copy() if request.GET else None
    if form_data is not None and not form_data.get("mode"):
        form_data["mode"] = "hybrid"
    form = DocumentSearchForm(form_data)
    results = []
    answer_evidence = []
    query = ""
    mode = "hybrid"
    elapsed_ms = None
    pending_documents = 0

    if request.GET and form.is_valid():
        query = form.cleaned_data["q"]
        mode = form.cleaned_data["mode"]
        try:
            results, elapsed_ms = retrieve_pages(request.user, query, mode, limit=30)
        except SemanticSearchUnavailable as exc:
            form.add_error(None, str(exc))
            query = ""
        else:
            answer_evidence = results[:3]

    pending_documents = Document.objects.filter(
        owner=request.user,
        extraction_status=Document.ExtractionStatus.PENDING,
    ).count()
    return render(request, "research/search_results.html", {
        "form": form,
        "query": query,
        "mode": mode,
        "results": results,
        "answer_evidence": answer_evidence,
        "elapsed_ms": elapsed_ms,
        "pending_documents": pending_documents,
    })


@login_required
def evaluation_dashboard(request):
    form = EvaluationCaseForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        case = form.save(commit=False)
        case.owner = request.user
        case.save()
        form.save_m2m()
        messages.success(request, "Labeled evaluation question added.")
        return redirect("evaluation_dashboard")

    cases = EvaluationCase.objects.filter(owner=request.user).prefetch_related(
        "relevant_pages__document"
    )
    case_count = cases.count()
    labeled_case_count = EvaluationCase.objects.filter(
        owner=request.user,
        relevant_pages__document__owner=request.user,
    ).distinct().count()
    available_page_count = ExtractedPage.objects.filter(
        document__owner=request.user,
    ).exclude(text="").count()
    runs = EvaluationRun.objects.filter(owner=request.user)[:10]

    return render(request, "research/evaluation_dashboard.html", {
        "form": form,
        "run_form": EvaluationRunForm(),
        "cases": cases,
        "case_count": case_count,
        "labeled_case_count": labeled_case_count,
        "unlabeled_case_count": case_count - labeled_case_count,
        "available_page_count": available_page_count,
        "runs": runs,
    })


@login_required
@require_POST
def delete_evaluation_case(request, pk):
    case = get_object_or_404(EvaluationCase, pk=pk, owner=request.user)
    case.delete()
    messages.success(request, "Evaluation question deleted.")
    return redirect("evaluation_dashboard")


@login_required
@require_POST
def run_evaluation(request):
    form = EvaluationRunForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Choose a value of k from 1 to 10.")
        return redirect("evaluation_dashboard")

    all_cases = list(
        EvaluationCase.objects
        .filter(owner=request.user)
        .prefetch_related("relevant_pages")
    )
    eligible_cases = [
        case for case in all_cases
        if case.relevant_pages.filter(document__owner=request.user).exists()
    ]
    ignored_unlabeled = len(all_cases) - len(eligible_cases)
    if not eligible_cases:
        messages.error(
            request,
            "Add at least one evaluation question and label its relevant source pages first.",
        )
        return redirect("evaluation_dashboard")

    try:
        report = build_evaluation_report(
            request.user,
            eligible_cases,
            form.cleaned_data["top_k"],
            ignored_unlabeled=ignored_unlabeled,
        )
    except SemanticSearchUnavailable as exc:
        messages.error(request, str(exc))
        return redirect("evaluation_dashboard")

    run = EvaluationRun.objects.create(
        owner=request.user,
        top_k=report["top_k"],
        question_count=report["query_count"],
        report=report,
    )
    messages.success(request, "Retrieval comparison completed.")
    return redirect("evaluation_run_detail", pk=run.pk)


@login_required
def evaluation_run_detail(request, pk):
    run = get_object_or_404(EvaluationRun, pk=pk, owner=request.user)
    methods = run.report.get("methods", [])
    max_latency = max(
        (method.get("mean_response_ms", 0) for method in methods),
        default=0,
    )
    chart_methods = []
    for method in methods:
        chart_methods.append({
            **method,
            "precision_percent": round(method.get("precision_at_k", 0) * 100, 1),
            "recall_percent": round(method.get("recall_at_k", 0) * 100, 1),
            "citation_percent": round(method.get("citation_accuracy", 0) * 100, 1),
            "mrr_percent": round(method.get("mrr", 0) * 100, 1),
            "latency_percent": (
                round(method.get("mean_response_ms", 0) / max_latency * 100, 1)
                if max_latency else 0
            ),
        })
    return render(request, "research/evaluation_run_detail.html", {
        "run": run,
        "methods": methods,
        "chart_methods": chart_methods,
        "questions": run.report.get("questions", []),
        "findings": run.report.get("findings", []),
        "ignored_unlabeled": run.report.get("ignored_unlabeled", 0),
    })

@login_required
def profile(request):
    # The post-save signal creates a profile for newly registered users.
    profile_obj = request.user.profile
    form = ProfileForm(request.POST or None, instance=profile_obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")
    return render(request, "research/profile.html", {"form": form})

@login_required
def upload_document(request):
    form = DocumentUploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        document = form.save(commit=False)
        document.owner = request.user
        try:
            extracted_pages, status, page_count, character_count = extract_uploaded_text(
                form.cleaned_data["file"]
            )
        except DocumentExtractionError as exc:
            form.add_error("file", str(exc))
        else:
            document.extraction_status = status
            document.page_count = page_count
            document.extracted_character_count = character_count
            try:
                with transaction.atomic():
                    document.save()
                    ExtractedPage.objects.bulk_create([
                        ExtractedPage(document=document, **page)
                        for page in extracted_pages
                    ])
            except Exception:
                if document.file and document.file.name:
                    document.file.delete(save=False)
                raise

            if status == Document.ExtractionStatus.NO_TEXT:
                messages.warning(
                    request,
                    "Document uploaded, but it contains no selectable text. "
                    "Scanned PDF pages need OCR, which is not included yet.",
                )
            else:
                messages.success(request, "Document uploaded and its text was extracted.")
            return redirect("document_detail", pk=document.pk)
    return render(request, "research/upload_document.html", {"form": form})

@login_required
def document_detail(request, pk):
    document = get_object_or_404(
        Document.objects.prefetch_related("extracted_pages"),
        pk=pk,
        owner=request.user,
    )
    return render(request, "research/document_detail.html", {
        "document": document,
        "extracted_pages": document.extracted_pages.all(),
    })

@login_required
@require_POST
def extract_document_text(request, pk):
    document = get_object_or_404(Document, pk=pk, owner=request.user)
    try:
        document.file.open("rb")
        try:
            extracted_pages, status, page_count, character_count = extract_uploaded_text(
                document.file,
                filename=document.filename,
            )
        finally:
            document.file.close()
    except (DocumentExtractionError, OSError, ValueError) as exc:
        message = str(exc) or "The original file could not be opened for extraction."
        messages.error(request, message)
        return redirect("document_detail", pk=document.pk)

    with transaction.atomic():
        document.extracted_pages.all().delete()
        ExtractedPage.objects.bulk_create([
            ExtractedPage(document=document, **page)
            for page in extracted_pages
        ])
        document.extraction_status = status
        document.page_count = page_count
        document.extracted_character_count = character_count
        document.save(update_fields=[
            "extraction_status",
            "page_count",
            "extracted_character_count",
        ])

    if status == Document.ExtractionStatus.NO_TEXT:
        messages.warning(
            request,
            "No selectable text was found. Scanned PDF pages need OCR, which is not included yet.",
        )
    else:
        messages.success(request, "Text extraction finished.")
    return redirect("document_detail", pk=document.pk)

@login_required
def open_document(request, pk):
    document = get_object_or_404(Document, pk=pk, owner=request.user)
    suffix = document.filename.rsplit(".", 1)[-1].lower() if "." in document.filename else ""
    content_type = "application/pdf" if suffix == "pdf" else "text/plain; charset=utf-8"
    response = FileResponse(
        document.file.open("rb"),
        as_attachment=False,
        filename=document.filename,
        content_type=content_type,
    )
    response["X-Content-Type-Options"] = "nosniff"
    return response

@login_required
@require_POST
def delete_document(request, pk):
    document = get_object_or_404(Document, pk=pk, owner=request.user)
    document.file.delete(save=False)
    document.delete()
    messages.success(request, "Document deleted.")
    return redirect("dashboard")
