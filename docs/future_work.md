# Future enhancements

The items below are proposed follow-up work, ordered by their effect on evidence coverage, retrieval quality, evaluation strength, and deployment readiness.

| Priority | Enhancement | Proposed work | How to evaluate it |
|---|---|---|---|
| 1 | OCR for scanned documents | Add OCR for image-only PDF pages, preserve page coordinates and confidence, and let users review extracted text. | Compare extraction coverage and OCR error rates against a manually transcribed sample. |
| 2 | Stronger retrieval evaluation | Collect a larger, diverse question set; document labeling guidance; add assessor agreement, confidence intervals, and paired significance tests. | Report reproducible scores with dataset and protocol details. |
| 3 | Scalable semantic index | Replace the per-request vector scan with a vector database or approximate-nearest-neighbor index and incremental updates. | Measure retrieval latency and recall as collection size increases. |
| 4 | Improved chunking and ranking | Add configurable overlapping chunks, section-aware parsing, metadata filters, and an optional cross-encoder reranker. | Compare retrieval quality and latency on the same labeled benchmark. |
| 5 | Grounded answer generation | Offer an optional language-model summary restricted to retrieved passages, with sentence-level citations and checks that each claim is supported. Keep extractive evidence available. | Human-review citation support, answer completeness, and unsupported-claim rates. |
| 6 | Broader document support | Add DOCX/HTML ingestion, multilingual embedding models, and richer metadata such as author, year, and DOI. | Validate extraction fidelity and retrieval quality by format and language. |
| 7 | Background processing | Move extraction and embedding work to a task queue with visible progress, retries, and failure recovery. | Test throughput, recovery behavior, and user-visible processing time. |
| 8 | Production security and operations | Add malware scanning, private object storage, quotas, audit events, secret management, backups, monitoring, and deployment configuration. | Complete a security review and operational recovery exercise. |
| 9 | Usability and accessibility | Improve keyboard navigation, screen-reader labels, mobile layouts, and export of evidence and evaluation reports. | Run accessibility checks and usability sessions with representative users. |

These proposals are not implemented features. Prioritize them after collecting feedback and measuring the current system on a manually labeled collection.
