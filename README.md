# Academic Research Assistant
## Evidence-Based Academic Research and Knowledge Assistant

A Django web application for managing academic PDFs/TXT files, extracting page-level text, retrieving evidence, and evaluating retrieval quality.

### Implemented modules

- Registration, login/logout, and user profile.
- Private document library (each user can access only their own documents).
- PDF/TXT upload (10 MB maximum) with validation.
- PDF text extraction by page using pypdf; TXT extraction as a single source.
- Document detail page showing extraction status and page text.
- Keyword search, optional local semantic search, and hybrid ranking.
- Evidence excerpts linked to the original document and page.
- Evaluation questions with manually labeled relevant pages.
- Saved comparisons for Precision@k, Recall@k, citation accuracy@3, MRR, and response time.
- Admin interface and SQLite default database; optional PostgreSQL configuration.
- Project report, architecture, test plan, demo guide, and submission checklist in `docs/`.

**Research integrity note:** retrieved excerpts are extractive evidence, not LLM-generated answers. Semantic search is optional and uses a local Sentence Transformers model. Scanned/image-only PDFs require OCR, which is not included. Evaluation findings are meaningful only after you create and label your own test questions and pages.

---

## 1. Windows CMD setup (recommended)

Open **Command Prompt (CMD)** and move into the extracted project folder. Example:

```cmd
cd /d "%USERPROFILE%\Downloads\Academic_Research_Assistant_Complete"
```

Create and activate a virtual environment:

```cmd
py -m venv .venv
.venv\Scripts\activate.bat
```

If Python 3.12 is not installed, check available versions:

```cmd
py -0p
```

For optional Sentence Transformers/PyTorch support, Python 3.11 or 3.12 is recommended. Your current Python version can be used for the core Django/PDF workflow if compatible packages install successfully.

Install the core dependencies:

```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Apply migrations and start the website:

```cmd
python manage.py check
python manage.py migrate
python manage.py runserver
```

Open:

- Website: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

Create your own account from the Register page. To create an admin account, stop the server with `Ctrl+C`, then run:

```cmd
python manage.py createsuperuser
```

Start the server again with `python manage.py runserver`.

### 2. Enable semantic and hybrid retrieval (optional)

Keyword search works with the core installation. To enable semantic/hybrid retrieval, install the optional model dependency:

```cmd
pip install -r requirements-semantic.txt
```

The first semantic/hybrid search downloads the model `sentence-transformers/all-MiniLM-L6-v2` and may take time. Internet access is required for the first download. The model runs locally on CPU by default. If model installation or loading fails, use Keyword mode.

Optional environment variables in CMD:

```cmd
set SEMANTIC_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
set SEMANTIC_DEVICE=cpu
python manage.py runserver
```

### 3. Optional PostgreSQL setup

SQLite is the default and requires no database setup. To use PostgreSQL, install its driver:

```cmd
pip install -r requirements-postgres.txt
```

Create an empty PostgreSQL database named `research_assistant`. Then set the connection variables in the same CMD window (replace the password):

```cmd
set DB_ENGINE=postgres
set PGDATABASE=research_assistant
set PGUSER=postgres
set PGPASSWORD=YOUR_POSTGRES_PASSWORD
set PGHOST=127.0.0.1
set PGPORT=5432
python manage.py migrate
python manage.py runserver
```

To return to SQLite in the current CMD window:

```cmd
set DB_ENGINE=
```

Do not share your database password or commit it to GitHub.

---

## 4. Main user workflow

1. Register a new account and sign in.
2. Open **Upload Document** and upload a selectable-text PDF or TXT file (maximum 10 MB).
3. Open the document details page and verify its extraction status and page text.
4. Open **Search**. Choose Keyword, Semantic, or Hybrid.
5. Review the ranked evidence excerpts and open the cited source document/page.
6. Open **Evaluation**. Add research questions and select the source pages that are relevant to each question.
7. Run the retrieval comparison and review the saved metrics and per-question results.

For a fair evaluation, label the same representative questions and relevant pages before comparing all retrieval methods. Record the documents, questions, model name, and `k` used.

## 5. Tests and verification

Run the automated test suite:

```cmd
python manage.py test research
```

Run project checks and migration checks:

```cmd
python manage.py check
python manage.py makemigrations --check --dry-run
```

The automated tests verify key workflows and access boundaries. Also follow `docs/test_cases.md` for manual browser checks. Record actual outcomes; do not mark unexecuted manual tests as passed.

## 6. Project structure

```text
config/          Django settings, ASGI/WSGI, root URLs
research/        Models, forms, views, extraction, retrieval, evaluation
research/migrations/
templates/       Django HTML templates
docs/            Report, architecture, test cases, demo, future work
media/           Uploaded files (created at runtime)
manage.py
requirements.txt
requirements-semantic.txt
requirements-postgres.txt
```

## 7. Important limitations and deployment notes

- OCR for scanned/image-only PDFs is not implemented.
- Generative LLM answers are not implemented; the app displays retrieved source excerpts.
- Embeddings are stored as JSON and scanned in application code. This is suitable for a small academic prototype, not a large-scale corpus.
- The evaluation dashboard does not create a ground-truth dataset automatically. A human must label relevant pages.
- Before public deployment, set a private `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=0`, configure `ALLOWED_HOSTS`, use HTTPS, secure uploaded-file serving, and configure production storage and database backups.
- The included development secret key is not suitable for deployment.

## 8. Submission documents

- `docs/PROJECT_REPORT.md` — project report draft.
- `docs/architecture.md` — architecture and sequence diagrams.
- `docs/test_cases.md` — manual functional test cases.
- `docs/demo_guide.md` — demonstration walkthrough.
- `docs/future_work.md` — limitations and enhancements.
- `docs/SUBMISSION_CHECKLIST.md` — final submission checklist.
- `docs/PHASE_SUMMARY.md` — summary of the integrated Phase 1–6 features.

The report intentionally does not invent evaluation scores. Complete the saved evaluation run and enter its actual results before final academic submission.
