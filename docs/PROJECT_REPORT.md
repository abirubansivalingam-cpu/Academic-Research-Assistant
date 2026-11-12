# Design and Development of an Evidence-Based Academic Research Assistant Using Hybrid Information Retrieval and Explainable AI

## Submission details

| Item | Details |
|---|---|
| Student | ABIRUBAN S |
| Programme / department | Master of Computer Applications (MCA) |
| Institution | Nandha Engineering College |
| Project guide | `[Guide name]` |
| Academic year | 2026 |

> Confirm the project guide details and replace the evaluation-results placeholders with values from a saved run in the application before submitting. Do not submit unmeasured or placeholder results as experimental findings.

## Abstract

Academic work often requires students to locate and verify information across research papers, lecture notes, and project documents. This project develops a web-based assistant that stores a user's academic documents, extracts PDF text with page references, and retrieves evidence using keyword, semantic, or hybrid search. The system presents retrieved excerpts with document and page citations. Its answer presentation is extractive: it quotes retrieved source text rather than generating unsupported claims.

The application uses Django for account and document workflows, SQLite by default with optional PostgreSQL, pypdf for PDF text extraction, and a locally running Sentence Transformers model for semantic embeddings. A research evaluation dashboard lets a user build a manually labeled question set and compare Keyword, Semantic, and Hybrid retrieval using Precision@k, Recall@k, citation accuracy@3, Mean Reciprocal Rank, and response time. It produces comparison charts and descriptive findings. The evaluation feature is implemented, but meaningful experimental results require a labeled dataset built from the user's document collection.

**Keywords:** academic research, information retrieval, semantic search, hybrid retrieval, evidence citations, explainable AI

## 1. Introduction

Academic materials are commonly spread across PDFs and text files. Keyword search can miss relevant passages when the question and document use different wording. Semantic retrieval can find passages with related meaning, but a result is harder to verify if it does not show where its evidence came from. The project addresses these issues by combining document management, page-level retrieval, and source-linked evidence.

### 1.1 Problem statement

Students spend time searching academic documents and checking whether an answer is supported by the supplied sources. A search result that does not retain page references adds extra work, while an ungrounded generated answer can be difficult to verify.

### 1.2 Aim

To design and develop a personal academic document assistant that retrieves relevant passages and makes their source locations visible, then measures how keyword, semantic, and hybrid retrieval perform on a labeled question set.

### 1.3 Objectives

1. Provide account registration, authentication, and personal profiles.
2. Accept PDF and TXT files and restrict each user's library to that user.
3. Extract PDF text by page and persist the text with page numbers.
4. Implement keyword, semantic, and hybrid retrieval over the stored text.
5. Present evidence excerpts with document and page links.
6. Provide a repeatable evaluation workflow with labeled relevant pages, comparison metrics, charts, and descriptive findings.

### 1.4 Research question

**Does hybrid retrieval improve the relevance and verifiability of academic document results compared with keyword-based retrieval on a manually labeled question set?**

The application's metrics support this comparison, but a conclusion should only be written after running the evaluation on a documented dataset.

## 2. Scope and limitations

The current implementation includes user registration, login and logout, profile management, private PDF/TXT uploads, PDF text extraction, text storage, keyword/semantic/hybrid retrieval, extractive evidence answers, and a retrieval evaluation dashboard.

The application does not perform OCR on scanned image-only PDFs and does not call a generative language model. Its evidence-linked answer consists of source excerpts with citations. Embeddings and similarity are scanned in application code and are suitable for a small document collection, not a large production corpus. The local-development settings require hardening before public deployment.

## 3. System design

The system is a Django web application. The browser sends requests to authenticated views. Forms validate user input and uploaded files. Django ORM stores users, profiles, document metadata, extracted page text, embeddings, evaluation questions, and saved evaluation reports. Original files are stored in media storage. The database is SQLite by default and can be configured for PostgreSQL.

PDF extraction runs during upload or when an existing document is explicitly processed. Each PDF page is stored separately with a one-based page number. A TXT upload is stored as one text record without a physical page number. Semantic embeddings are generated locally when semantic or hybrid retrieval is first used and are saved with their model name. An embedding-model change triggers a rebuild on the next semantic or hybrid search.

See [architecture diagrams](architecture.md) for the component graph and request sequences.

### 3.1 Retrieval methods

- **Keyword retrieval:** matches query terms against extracted page text and ranks pages by term coverage and frequency.
- **Semantic retrieval:** embeds query and page-text chunks and ranks by cosine similarity. Stored vectors are normalized, so the implementation uses a dot product.
- **Hybrid retrieval:** combines the keyword and semantic scores with equal weights: `0.5 × keyword + 0.5 × max(cosine similarity, 0)`.

### 3.2 Evidence-linked answer

The highest-ranked passages are shown as excerpts with links to the source document and page. The answer is extractive rather than LLM-generated; each excerpt can be checked against its source. The system does not claim that an excerpt fully answers a question merely because it was retrieved.

## 4. Implementation methodology

The project was developed incrementally. Phase 1 established accounts, profiles, document upload, and a private library. Phase 2 added text extraction and page-level text storage. Phase 3 added keyword retrieval and matching excerpts. Phase 4 introduced local semantic embeddings, hybrid scoring, and evidence-linked answers. Phase 5 added manually labeled evaluation, comparison metrics, charts, and generated descriptive findings. Phase 6 packages the report, architecture diagrams, test plan, demonstration guide, and future-work plan.

The upload workflow validates the file extension and size, checks the basic PDF signature, extracts text, and saves the original file and extracted page records. A scanned PDF with no selectable text is retained and marked as having no text; OCR is outside the current scope.

The evaluation workflow asks a reviewer to create questions and label relevant source pages. All methods run against the same questions and labels. The evaluation runner warms up each method before recording response time, excluding first-use model loading and embedding-index construction from those latency measurements.

## 5. Evaluation methodology

### 5.1 Dataset protocol

Create a small collection of representative academic documents. Prepare questions that cover direct terminology matches, paraphrases, and questions with evidence on multiple pages. For every question, manually label all pages considered relevant. Use the same labeled questions for all three retrieval methods. Record the document set, question set, model name, `k`, and any exclusion criteria in the final report.

### 5.2 Metrics

Let `R_q` be the set of labeled relevant pages for question `q`, and let `T_q(k)` be the first `k` retrieved pages.

- **Precision@k:** `|T_q(k) ∩ R_q| / k`. The denominator remains `k` if fewer than `k` pages are returned.
- **Recall@k:** `|T_q(k) ∩ R_q| / |R_q|`.
- **Citation accuracy@3:** fraction of the up to three answer passages that point to a labeled relevant page. It is zero when there are no cited passages.
- **MRR@k:** reciprocal rank of the first relevant result within the first `k`, or zero if none is relevant.
- **Mean response time:** average measured retrieval duration in milliseconds per question and method. First-use model/index setup is excluded.

Reported quality metrics are macro-averaged over questions. The evaluation dashboard also saves per-question results so aggregate scores can be inspected.

## 6. Results and discussion

No empirical values are included in this report because the project has not been run against a user-labeled document set in this workspace. Do not treat the automatically generated findings as research evidence until a labeled evaluation run has been completed and reviewed.

After running a comparison, copy the values from the saved evaluation report into this table:

| Retrieval method | Precision@k | Recall@k | Citation accuracy@3 | MRR@k | Mean response time (ms) |
|---|---:|---:|---:|---:|---:|
| Keyword | `[value]` | `[value]` | `[value]` | `[value]` | `[value]` |
| Semantic | `[value]` | `[value]` | `[value]` | `[value]` | `[value]` |
| Hybrid | `[value]` | `[value]` | `[value]` | `[value]` | `[value]` |

Discuss which method performed best for precision, recall, citation accuracy, and latency. Explain cases where a method retrieved an irrelevant page or missed a labeled page. Relate the findings to the document collection and question design. The current dashboard produces descriptive comparisons only; it does not calculate confidence intervals or statistical significance.

## 7. Test plan

Functional test cases cover account workflows, document validation and ownership, PDF/TXT extraction, page references, each retrieval mode, citation links, evaluation labels, metrics, and saved report access. See [test cases](test_cases.md). The cases in that document are marked **Not run** until executed in a local Python environment with prepared sample files and evaluation labels.

## 8. Demonstration

The [demonstration guide](demo_guide.md) provides a short walkthrough: register, upload documents, inspect extracted text, compare retrieval modes, label relevant pages, run evaluation, and present the saved charts and findings.

## 9. Conclusion

The project delivers a full-stack document assistant that connects document upload and text extraction with keyword, semantic, and hybrid retrieval. Page-level storage makes results easier to trace to source material. The evaluation dashboard provides a repeatable way to compare retrieval approaches on manually labeled questions. The research conclusion remains dependent on collecting representative documents, labeling relevant pages, and running the evaluation.

## 10. Future enhancements

Prioritized future work is listed in [future enhancements](future_work.md). The main items are OCR, a dedicated vector database for larger collections, improved chunking and reranking, an optional constrained generative answer layer, richer statistical evaluation, and production hardening.

## References

1. Django Software Foundation. *Using the Django authentication system*. <https://docs.djangoproject.com/en/5.2/topics/auth/default/>.
2. Django Software Foundation. *Testing tools*. <https://docs.djangoproject.com/en/5.1/topics/testing/tools/>.
3. pypdf. *Page text extraction API*. <https://pypdf.readthedocs.io/en/latest/page.html>.
4. Sentence Transformers. *Semantic Search*. <https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html>.
