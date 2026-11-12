# Demonstration guide

## Purpose

Show the complete path from private document upload to traceable retrieval and a reproducible comparison of retrieval methods. Plan for approximately 6–8 minutes. Use only documents you are allowed to demonstrate.

## Before the demonstration

1. Install dependencies, run database migrations, and start the Django server using the README instructions.
2. Prepare two text-based PDFs with selectable text and at least two pages, plus one TXT file. Include one exact keyword match and one paraphrase example.
3. Create a demo account and upload those files. For the evaluation section, create at least three questions and manually label relevant pages.
4. If Semantic or Hybrid retrieval has not been used before, allow time for the Sentence Transformers model to download and the page embeddings to be created. Use Keyword mode if the model cannot be loaded.
5. Do not present evaluation numbers as findings until the labeled set and saved report have been reviewed. This workspace contains no experimental results.

## Walkthrough

| Time | Action | What to explain |
|---|---|---|
| 0:00–0:45 | Introduce the research problem and project goal. | The assistant helps find evidence in a personal academic document collection and keeps source page references visible. |
| 0:45–1:30 | Register or sign in; open the document library. | Accounts scope the document library to its owner. |
| 1:30–2:30 | Upload a PDF and a TXT file; open a document detail page. | PDFs are extracted page by page with pypdf. TXT has no physical page number. Image-only scanned PDFs need OCR, which is future work. |
| 2:30–4:00 | Run the same query in Keyword, Semantic, and Hybrid modes. | Keyword matches terms; Semantic compares locally generated embeddings; Hybrid combines keyword and semantic scores. Show excerpts, source documents, and page links. |
| 4:00–4:45 | Open a result citation and the evidence-linked answer. | The answer is extractive: it presents retrieved evidence passages with source links rather than generating unsupported claims. |
| 4:45–6:30 | Open Evaluation, inspect labeled questions, and run the three methods at the same k. | Relevant pages are human labels. The dashboard reports P@k, R@k, citation accuracy@3, MRR@k, mean response time, charts, and per-question results. |
| 6:30–7:30 | Show the saved comparison and explain the limits. | Interpret only results from this actual labeled set. The report is descriptive and does not test statistical significance. |

## Suggested example queries

Replace these examples with queries that match the prepared documents:

- **Exact term:** a phrase that occurs verbatim in one PDF.
- **Paraphrase:** a question that describes a concept using different wording from the source.
- **Multi-page question:** a question with relevant evidence on more than one page.

## Closing points

- Evidence can be traced to a user's stored document and page.
- The three retrieval methods can be compared on the same manually labeled questions.
- The prototype currently relies on selectable PDF text and a local vector scan; OCR and scalable vector indexing are future enhancements.

## Demo record

Record the environment, document set, model name, question count, relevant-page labeling procedure, k, and any issues encountered. Capture screenshots of the document page, a cited search result, and the saved evaluation charts for the final presentation if required.
