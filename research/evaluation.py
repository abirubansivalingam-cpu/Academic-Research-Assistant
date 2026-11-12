from .retrieval import RETRIEVAL_MODES, retrieve_pages


METHOD_LABELS = {
    "keyword": "Keyword",
    "semantic": "Semantic",
    "hybrid": "Hybrid",
}


def _query_metrics(results, relevant_page_ids, top_k):
    top_results = results[:top_k]
    retrieved_ids = [result["page"].pk for result in top_results]
    relevant_hits = sum(page_id in relevant_page_ids for page_id in retrieved_ids)
    precision = relevant_hits / top_k
    recall = relevant_hits / len(relevant_page_ids) if relevant_page_ids else 0.0

    citation_results = results[:3]
    citation_hits = sum(
        result["page"].pk in relevant_page_ids
        for result in citation_results
    )
    citation_accuracy = (
        citation_hits / len(citation_results) if citation_results else 0.0
    )

    reciprocal_rank = 0.0
    for rank, result in enumerate(top_results, start=1):
        if result["page"].pk in relevant_page_ids:
            reciprocal_rank = 1 / rank
            break

    return {
        "precision_at_k": precision,
        "recall_at_k": recall,
        "citation_accuracy": citation_accuracy,
        "mrr": reciprocal_rank,
        "relevant_hits": relevant_hits,
    }


def _mean(values):
    return sum(values) / len(values) if values else 0.0


def _winner(methods, metric, maximize=True):
    if not methods:
        return "No method", 0.0
    best_value = (max if maximize else min)(method[metric] for method in methods)
    winners = [
        method["label"]
        for method in methods
        if abs(method[metric] - best_value) < 0.0001
    ]
    return " and ".join(winners), best_value


def build_evaluation_report(user, cases, top_k, ignored_unlabeled=0):
    """Compare all retrieval modes on the same manually labeled cases.

    The warm-up retrieves once per method before measuring response time. This
    excludes first-use model loading and embedding generation from query latency.
    """
    cases = list(cases)
    if not cases:
        raise ValueError("Add at least one question with a relevant page label first.")

    limit = max(top_k, 3)
    warmup_query = cases[0].question
    for mode in RETRIEVAL_MODES:
        retrieve_pages(user, warmup_query, mode, limit=limit)

    question_reports = []
    per_method = {mode: [] for mode in RETRIEVAL_MODES}

    for case in cases:
        relevant_pages = list(
            case.relevant_pages
            .filter(document__owner=user)
            .select_related("document")
        )
        relevant_page_ids = {page.pk for page in relevant_pages}
        method_reports = {}

        for mode in RETRIEVAL_MODES:
            results, elapsed_ms = retrieve_pages(
                user,
                case.question,
                mode,
                limit=limit,
            )
            metrics = _query_metrics(results, relevant_page_ids, top_k)
            method_report = {
                **metrics,
                "response_ms": elapsed_ms,
                "retrieved": [
                    {
                        "title": result["document"].title,
                        "document_id": result["document"].pk,
                        "page_id": result["page"].pk,
                        "page_number": result["page"].page_number,
                        "page_label": (
                            f"Page {result['page'].page_number}"
                            if result["page"].page_number
                            else "TXT document"
                        ),
                        "relevant": result["page"].pk in relevant_page_ids,
                        "score": result["score"],
                        "excerpt": result["excerpt"],
                    }
                    for result in results[:max(top_k, 3)]
                ],
            }
            method_reports[mode] = method_report
            per_method[mode].append(method_report)

        question_reports.append({
            "question": case.question,
            "relevant_page_count": len(relevant_page_ids),
            "methods": [
                {
                    "key": mode,
                    "label": METHOD_LABELS[mode],
                    **method_reports[mode],
                }
                for mode in RETRIEVAL_MODES
            ],
        })

    method_summaries = []
    for mode in RETRIEVAL_MODES:
        query_metrics = per_method[mode]
        method_summaries.append({
            "key": mode,
            "label": METHOD_LABELS[mode],
            "precision_at_k": round(_mean([m["precision_at_k"] for m in query_metrics]), 4),
            "recall_at_k": round(_mean([m["recall_at_k"] for m in query_metrics]), 4),
            "citation_accuracy": round(_mean([m["citation_accuracy"] for m in query_metrics]), 4),
            "mrr": round(_mean([m["mrr"] for m in query_metrics]), 4),
            "mean_response_ms": round(_mean([m["response_ms"] for m in query_metrics]), 2),
        })

    findings = []
    precision_winner, precision = _winner(method_summaries, "precision_at_k")
    recall_winner, recall = _winner(method_summaries, "recall_at_k")
    citation_winner, citation = _winner(method_summaries, "citation_accuracy")
    latency_winner, latency = _winner(method_summaries, "mean_response_ms", maximize=False)
    findings.extend([
        f"{precision_winner} had the highest mean Precision@{top_k} ({precision:.1%}).",
        f"{recall_winner} had the highest mean Recall@{top_k} ({recall:.1%}).",
        f"{citation_winner} had the highest citation accuracy@3 ({citation:.1%}).",
        f"{latency_winner} had the lowest mean retrieval time ({latency:.1f} ms).",
        (
            f"Results use {len(cases)} manually labeled question(s) and are descriptive; "
            "they are not a statistical significance test."
        ),
    ])

    return {
        "top_k": top_k,
        "query_count": len(cases),
        "ignored_unlabeled": ignored_unlabeled,
        "methods": method_summaries,
        "questions": question_reports,
        "findings": findings,
    }
