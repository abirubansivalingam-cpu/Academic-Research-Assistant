from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


class DocumentExtractionError(Exception):
    """Raised when an uploaded document cannot be converted into text."""


def extract_uploaded_text(uploaded_file, filename=None):
    """Extract TXT as one source and PDF text page-by-page with page numbers."""
    suffix = Path(filename or uploaded_file.name).suffix.lower()
    uploaded_file.seek(0)
    raw_data = uploaded_file.read()
    uploaded_file.seek(0)

    if suffix == ".txt":
        try:
            text = raw_data.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw_data.decode("latin-1")
        pages = [{"page_number": None, "text": text}]
        status = "completed" if text.strip() else "no_text"
        return pages, status, 0, len(text)

    if suffix != ".pdf":
        raise DocumentExtractionError("Only PDF and TXT files can be processed.")

    try:
        reader = PdfReader(BytesIO(raw_data), strict=False)
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception as exc:
                raise DocumentExtractionError(
                    "This PDF is encrypted. Upload an unlocked PDF."
                ) from exc
        pages = [
            {
                "page_number": index + 1,
                "text": (page.extract_text() or "").strip(),
            }
            for index, page in enumerate(reader.pages)
        ]
    except DocumentExtractionError:
        raise
    except Exception as exc:
        raise DocumentExtractionError(
            "This PDF could not be read. Check that it is a valid PDF."
        ) from exc

    character_count = sum(len(page["text"]) for page in pages)
    status = "completed" if character_count else "no_text"
    return pages, status, len(pages), character_count
