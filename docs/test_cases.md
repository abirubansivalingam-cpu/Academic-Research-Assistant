# Functional test cases

These are manual functional test cases for the Phase 6 submission. Record the actual date, tester, environment, and outcome before submission. All cases are **Not run** in the packaged workspace.

## Test setup

1. Install the project and run `python manage.py migrate`.
2. Start the server and create two accounts, **User A** and **User B**.
3. Prepare two text-based PDFs with at least two pages each, one TXT file, one scanned/image-only PDF, one unsupported file type, and one file larger than 10 MB.
4. Ensure one PDF contains an exact keyword query and another contains semantically related wording with little or no lexical overlap.
5. Upload the searchable documents as User A. Extract text from existing Phase 1 documents if needed.
6. For evaluation tests, label at least three questions with relevant source pages, including one question whose relevant page uses a paraphrase.

## Functional cases

| ID | Priority | Test case and steps | Expected result | Status |
|---|---|---|---|---|
| TC-01 | High | Register User A with a valid username, email, and matching valid passwords. Log out and log back in. | Account is created; password is not displayed or stored as plain text; login/logout work. | Not run |
| TC-02 | Medium | Register a second account using User A's email with different capitalization. | Registration is rejected with a duplicate-email error. | Not run |
| TC-03 | High | While logged out, request `/dashboard/`, `/search/`, and `/evaluation/`. | Each protected page redirects to login. | Not run |
| TC-04 | High | As User A, upload an unsupported file and a file over 10 MB. | Both uploads are rejected with a field error; no document is added. | Not run |
| TC-05 | High | Upload a valid two-page PDF with selectable text. Open its document details. | Original file is stored; extracted text is visible under the correct one-based page numbers; page count and character count are shown. | Not run |
| TC-06 | Medium | Upload a UTF-8 TXT file containing a known phrase. Open extracted text and search for the phrase. | Text is stored as a TXT record without a physical page number; search result is labeled TXT document. | Not run |
| TC-07 | Medium | Upload a scanned PDF containing only page images. | PDF is retained, extraction status reports no selectable text, and OCR limitation is explained. | Not run |
| TC-08 | High | As User B, try to open a User A document detail, original file URL, or evaluation report by changing its numeric ID. | User B cannot access User A's document, file, extracted text, or report. | Not run |
| TC-09 | High | As User A, search for an exact word that appears on a known PDF page using Keyword mode. | The matching page appears with an excerpt and the correct document/page link. | Not run |
| TC-10 | High | Search a paraphrased question with little lexical overlap using Semantic mode after the model is available. | A semantically related passage is ranked and cited, even without an exact keyword match. | Not run |
| TC-11 | High | Repeat a query using Hybrid mode. | Keyword and semantic candidates are ranked by the documented hybrid score; a keyword match and a semantic-only match can both appear. | Not run |
| TC-12 | High | Open a result's document/page link from search and from the evidence-linked answer. | The link opens the matching document detail page and anchors to the cited page or TXT text. | Not run |
| TC-13 | High | In Evaluation, add a question and select one or more relevant pages. Attempt to select a page owned by User B through a modified request. | User A can label only User A pages; saved case displays its selected labels. | Not run |
| TC-14 | High | Create at least three labeled questions, choose `k=3`, and run all methods. | Keyword, Semantic, and Hybrid run on the same labeled questions and same k; one saved report is created. | Not run |
| TC-15 | High | Inspect aggregate report values for P@k, R@k, Citation accuracy@3, MRR@k, and response time. Compare one question manually against its retrieved pages and labels. | Metrics follow the definitions in the report; citation accuracy counts relevant pages among up to three cited passages; P@k uses k as denominator. | Not run |
| TC-16 | Medium | Inspect comparison charts, findings, and per-question results. Refresh the report page. | Charts correspond to saved aggregate metrics; findings identify metric leaders; per-question excerpts and relevance labels persist after refresh. | Not run |
| TC-17 | Medium | Add an unlabeled evaluation question and run a comparison. Then try running with no labeled questions. | Unlabeled cases are skipped and counted; with no eligible cases, the user gets a clear message and no empty report is created. | Not run |
| TC-18 | Medium | Make the semantic model unavailable (for example, block model download) and try Semantic/Hybrid search, then Keyword search. | Semantic/Hybrid show a model setup error; Keyword search remains usable. | Not run |
| TC-19 | Medium | Migrate an existing Phase 1 database containing a pending document. Open its details and choose Extract text. | Existing source file is processed and page text is stored; the document becomes searchable. | Not run |

## Acceptance criteria

- Every test marked High passes before the live demonstration.
- No user can retrieve another user's documents, extracted text, labels, or evaluation runs.
- Search citations resolve to the source document and the correct page or TXT record.
- Evaluation results can be repeated against the same saved labeled set and retrieval settings.
- Any failed case is recorded with the reproduction steps and corrected before final submission, or listed as a known limitation.

## Execution record

| Tester | Date | Python / Django version | Cases passed | Cases failed | Notes |
|---|---|---|---:|---:|---|
| `[Name]` | `[Date]` | `[Versions]` | `[ ]` | `[ ]` | `[Notes]` |
