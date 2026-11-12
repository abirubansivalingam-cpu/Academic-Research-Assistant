from functools import lru_cache

from django.conf import settings
from .models import ExtractedPage


class SemanticSearchUnavailable(Exception):
    """Raised when the local embedding model cannot be loaded or used."""


def get_model_name():
    return getattr(
        settings,
        "SEMANTIC_EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )


@lru_cache(maxsize=2)
def _load_model(model_name):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise SemanticSearchUnavailable(
            "Semantic search requires the sentence-transformers package. "
            "Install the project's requirements and try again."
        ) from exc

    try:
        return SentenceTransformer(
            model_name,
            device=getattr(settings, "SEMANTIC_DEVICE", "cpu"),
        )
    except Exception as exc:
        raise SemanticSearchUnavailable(
            "The semantic model could not be loaded. Check the model setting and "
            "network access for its first download."
        ) from exc


def _split_text(text, max_characters=900):
    normalized = " ".join(text.split())
    chunks = []
    start = 0
    while start < len(normalized):
        end = min(start + max_characters, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", start, end)
            if boundary > start:
                end = boundary
        chunks.append(normalized[start:end])
        start = end
        while start < len(normalized) and normalized[start].isspace():
            start += 1
    return chunks


def _encode(model, texts):
    if not texts:
        return []
    try:
        vectors = model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
    except Exception as exc:
        raise SemanticSearchUnavailable(
            "The semantic model could not encode this search. Try keyword search "
            "or check the local model installation."
        ) from exc
    return [[float(value) for value in vector] for vector in vectors]


def prepare_user_pages(user):
    """Load a user's text pages and lazily create missing page-chunk vectors."""
    pages = list(
        ExtractedPage.objects
        .filter(document__owner=user)
        .exclude(text="")
        .select_related("document")
        .order_by("-document__uploaded_at", "document_id", "page_number")
    )
    pages = [page for page in pages if page.text.strip()]
    if not pages:
        return pages, None

    model_name = get_model_name()
    model = _load_model(model_name)
    stale_pages = [
        page for page in pages
        if page.embedding_model != model_name or not page.embeddings or not page.embedding_texts
    ]
    if stale_pages:
        chunks = []
        chunk_owners = []
        chunks_by_page = {page.pk: [] for page in stale_pages}
        for page in stale_pages:
            for chunk in _split_text(page.text):
                chunks.append(chunk)
                chunk_owners.append(page.pk)
                chunks_by_page[page.pk].append(chunk)

        vectors = _encode(model, chunks)
        vectors_by_page = {page.pk: [] for page in stale_pages}
        for page_id, vector in zip(chunk_owners, vectors):
            vectors_by_page[page_id].append(vector)

        for page in stale_pages:
            page.embedding_texts = chunks_by_page[page.pk]
            page.embeddings = vectors_by_page[page.pk]
            page.embedding_model = model_name
        ExtractedPage.objects.bulk_update(
            stale_pages,
            ["embedding_texts", "embeddings", "embedding_model"],
            batch_size=100,
        )

    return pages, model


def encode_query(model, query):
    vectors = _encode(model, [query])
    return vectors[0] if vectors else []


def page_similarity(query_vector, page):
    """Cosine similarity via dot product; stored vectors are normalized."""
    if not query_vector or not page.embeddings:
        return -1.0, page.text
    scores = [
        sum(query_value * chunk_value for query_value, chunk_value in zip(query_vector, chunk_vector))
        for chunk_vector in page.embeddings
    ]
    best_index = max(range(len(scores)), key=scores.__getitem__)
    evidence_text = (
        page.embedding_texts[best_index]
        if best_index < len(page.embedding_texts)
        else page.text
    )
    return scores[best_index], evidence_text
