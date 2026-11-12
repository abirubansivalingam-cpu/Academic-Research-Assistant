import re
import time

from django.db.models import Q

from .models import ExtractedPage
from .semantic_search import (
    encode_query,
    page_similarity,
    prepare_user_pages,
)


RETRIEVAL_MODES = ("keyword", "semantic", "hybrid")


def _make_excerpt(text, terms, context=100):
    lowered = text.casefold()
    matches = [
        (lowered.find(term.casefold()), term)
        for term in terms
        if lowered.find(term.casefold()) >= 0
    ]
    if matches:
        position, term = min(matches, key=lambda match: match[0])
        start = max(0, position - context)
        end = min(len(text), position + len(term) + context)
    else:
        start = 0
        end = min(len(text), 260)
    excerpt = text[start:end].strip()
    if start:
        excerpt = "…" + excerpt
    if end < len(text):
        excerpt += "…"
    return excerpt


def retrieve_pages(user, query, mode, limit=30):
    """Retrieve and rank text pages for one user; return results and elapsed ms."""
    if mode not in RETRIEVAL_MODES:
        raise ValueError(f"Unsupported retrieval mode: {mode}")

    started = time.perf_counter()
    terms = list(dict.fromkeys(re.findall(r"\w+", query, flags=re.UNICODE)))
    keyword_filter = Q()
    for term in terms:
        keyword_filter |= Q(text__icontains=term)

    query_vector = None
    if mode == "keyword":
        pages = list(
            ExtractedPage.objects
            .filter(document__owner=user)
            .exclude(text="")
            .filter(keyword_filter)
            .select_related("document")
            .order_by("-document__uploaded_at", "document_id", "page_number")
        ) if terms else []
    else:
        pages, model = prepare_user_pages(user)
        query_vector = encode_query(model, query) if model else []

    results = []
    for page in pages:
        lowered = page.text.casefold()
        matched_terms = [term for term in terms if term.casefold() in lowered]
        if mode == "keyword" and not matched_terms:
            continue

        match_count = sum(lowered.count(term.casefold()) for term in matched_terms)
        keyword_score = 0.0
        if matched_terms:
            coverage = len(matched_terms) / len(terms)
            frequency = min(match_count / (3 * len(terms)), 1.0)
            keyword_score = 0.7 * coverage + 0.3 * frequency

        semantic_score = None
        evidence_text = page.text
        if query_vector:
            semantic_score, semantic_evidence = page_similarity(query_vector, page)
            if not matched_terms:
                evidence_text = semantic_evidence

        if mode == "semantic":
            if semantic_score is None or semantic_score < 0.15:
                continue
            rank_score = semantic_score
        elif mode == "hybrid":
            semantic_component = min(max(semantic_score or 0.0, 0.0), 1.0)
            if not matched_terms and semantic_component < 0.15:
                continue
            rank_score = 0.5 * keyword_score + 0.5 * semantic_component
        else:
            rank_score = keyword_score

        results.append({
            "page": page,
            "document": page.document,
            "excerpt": _make_excerpt(evidence_text, matched_terms),
            "matched_terms": len(matched_terms),
            "match_count": match_count,
            "keyword_score": keyword_score,
            "semantic_score": semantic_score,
            "score": rank_score,
        })

    results.sort(
        key=lambda result: (
            result["score"],
            result["matched_terms"],
            result["match_count"],
        ),
        reverse=True,
    )
    elapsed_ms = (time.perf_counter() - started) * 1000
    return results[:limit], elapsed_ms
