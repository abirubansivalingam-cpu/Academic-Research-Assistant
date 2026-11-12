# Architecture diagrams

## Component architecture

```mermaid
flowchart LR
    Browser[Browser UI]
    Router[Django URL routing]
    Views[Authenticated Django views]
    Forms[Forms and input validation]
    Retrieval[Keyword / semantic / hybrid retrieval]
    Evaluation[Evaluation runner and metrics]
    Extract[pypdf text extraction]
    Embed[Sentence Transformers model]
    DB[(SQLite or PostgreSQL)]
    Files[(Private media storage)]

    Browser --> Router --> Views
    Views --> Forms
    Views --> Retrieval
    Views --> Evaluation
    Views --> Extract
    Extract --> DB
    Extract --> Files
    Retrieval --> DB
    Retrieval --> Embed
    Embed --> DB
    Evaluation --> Retrieval
    Evaluation --> DB
```

The browser sends requests to Django. Views require a signed-in user for document, search, and evaluation operations. Django ORM stores accounts, document metadata, extracted page text, embeddings, labeled questions, and saved evaluation reports. Original uploads are stored under the configured media storage. PDF text is extracted with pypdf; semantic embeddings are generated locally with Sentence Transformers.

## Upload and extraction sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as Django upload form
    participant View as Upload view
    participant PDF as pypdf
    participant DB as Database
    participant Store as Media storage

    User->>UI: Submit PDF or TXT
    UI->>View: Authenticated multipart POST
    View->>View: Validate owner, extension, and size
    View->>PDF: Extract text by page (PDF)
    PDF-->>View: Page text and page numbers
    View->>Store: Save original file
    View->>DB: Save document and extracted text atomically
    DB-->>UI: Redirect to document details
    UI-->>User: Show extracted text and source pages
```

## Retrieval and evaluation sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as Search / evaluation page
    participant View as Django view
    participant Retrieval as Shared retrieval service
    participant Model as Local embedding model
    participant DB as Database

    User->>UI: Enter question and retrieval mode
    UI->>View: GET search request
    View->>Retrieval: Retrieve owner-scoped pages
    alt Keyword mode
        Retrieval->>DB: Filter extracted text by keywords
    else Semantic or hybrid mode
        Retrieval->>DB: Load page text and stored vectors
        Retrieval->>Model: Encode query
        Model-->>Retrieval: Query vector
        Retrieval->>Retrieval: Rank by cosine similarity / hybrid score
    end
    Retrieval-->>View: Ranked excerpts and page references
    View-->>UI: Evidence-linked answer and results

    User->>UI: Run labeled evaluation
    UI->>View: POST top-k comparison
    View->>Retrieval: Run each method on the same questions
    Retrieval-->>View: Results and measured latency
    View->>DB: Save metrics, findings, and report snapshot
    View-->>UI: Charts and per-question comparisons
```

## Retrieval score definitions

- **Keyword:** query tokens are matched against extracted page text. The score combines query-term coverage and match frequency.
- **Semantic:** normalized query and page-chunk embeddings are compared by cosine similarity. Since vectors are normalized, the implementation uses their dot product.
- **Hybrid:** `0.5 × keyword score + 0.5 × max(cosine similarity, 0)`.

The current exact vector scan is intended for a small research collection. A larger deployment should replace it with an approximate-nearest-neighbor index.
