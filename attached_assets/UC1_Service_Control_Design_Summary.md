# C) Service / Control Design Summary

## UC1 — RewriteTextToReadingLevel

### Architecture (minimal layers)

```
React Client                  FastAPI Server                     External
+-----------+                 +----------------------------+     +-------------------+
|           |    HTTP         |  POST /api/rewrite         |     |                   |
| Rewrite   | ──────────────▶ |  POST /api/documents/      |     |  StyleRewriter    |
| Page      |                 |       {id}/versions        |     |  (Anthropic       |
|           |                 |                            |     |   Claude)         |
+-----------+                 |  RewriteService            |     |                   |
                              |    │                       |     +-------------------+
                              |    ├──▶ DocumentRepository |            ▲
                              |    ├──▶ VersionRepository  |            │
                              |    └──▶ StyleRewriterPort ─┤── adapter ─┘
                              |                            |
                              +----------------------------+
                                         │
                                         ▼
                                    PostgreSQL DB
```

---

### Application Service: `RewriteService`

| Method | Signature | Behaviour | Scenarios |
|---|---|---|---|
| `rewrite_text` | `(text: str, reading_level: str) → RewriteResult` | Validates input → calls StyleRewriter → returns `RewriteResult(original, rewritten, reading_grade)` | S01, S03, S04, S09, S10, S16, S17 |
| `save_version` | `(document_id: UUID, content: str, reading_level: str, author: str) → DocumentVersion` | Creates a new `document_versions` row with next `version_number` | S02, S12, S13 |

#### `RewriteResult` (Pydantic schema)

```python
class RewriteResult(BaseModel):
    original_text: str
    rewritten_text: str
    reading_grade: float       # Flesch-Kincaid grade level of output
    target_reading_level: str  # echoed back
```

#### Validation rules (inside `rewrite_text`)

| Rule | Error raised | HTTP status | Scenarios |
|---|---|---|---|
| `text` is empty or whitespace-only | `ValidationError("source_text_empty")` | 422 | S06, S07 |
| `reading_level` is empty or not in allowed set | `ValidationError("reading_level_required")` | 422 | S08 |

---

### External Dependency: `StyleRewriterPort` (adapter interface)

```python
class StyleRewriterPort(ABC):
    @abstractmethod
    async def rewrite(self, text: str, target_level: str) -> str:
        """Returns rewritten text or raises StyleRewriterError."""
```

---

### Real Adapter: `AnthropicStyleRewriter`

| Concern | Detail |
|---|---|
| Provider | Anthropic Claude (via `anthropic` SDK) |
| Input | Source text + target reading level |
| Output | Rewritten text string |
| Error: unclear text | Raises `UnclearTextError` when Claude signals inability to safely rewrite |
| Error: service down | Raises `ServiceUnavailableError` on network/5xx failures |

---

### Test Double: `FakeStyleRewriter`

| Behaviour | Implementation | Scenarios |
|---|---|---|
| Normal rewrite | Returns a deterministic simplified string; `textstat.flesch_kincaid_grade()` yields a grade within ±1 of target | S01–S04, S11–S14, S16, S17 |
| Unclear text | If input contains a sentinel phrase (e.g., `"UNCLEAR_SENTINEL"`), raises `UnclearTextError` | S09, S15 |
| Service unavailable | If configured with `simulate_outage=True`, raises `ServiceUnavailableError` | S10 |

---

### API Endpoints

| Method | Path | Request Body | Response | Status Codes |
|---|---|---|---|---|
| `POST` | `/api/rewrite` | `{ "text": str, "reading_level": str }` | `RewriteResult` | 200, 422 (validation), 502 (unclear text), 503 (service down) |
| `POST` | `/api/documents/{id}/versions` | `{ "content": str, "reading_level": str, "author": str }` | `DocumentVersion` | 201, 404 (doc not found) |
| `GET` | `/api/documents/{id}/versions` | — | `List[DocumentVersion]` | 200, 404 |
| `GET` | `/api/documents/{id}` | — | `Document` | 200, 404 |
