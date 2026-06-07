# B) Database Design Summary

## UC1 — RewriteTextToReadingLevel

### Entity-Relationship Diagram

```
DOCUMENTS ||--o{ DOCUMENT_VERSIONS : "has versions"

DOCUMENTS:
  - id          (UUID, PK)
  - title       (TEXT)
  - content     (TEXT)
  - created_at  (TIMESTAMPTZ)
  - updated_at  (TIMESTAMPTZ)

DOCUMENT_VERSIONS:
  - id              (UUID, PK)
  - document_id     (UUID, FK → documents.id)
  - version_number  (INTEGER)
  - content         (TEXT)
  - reading_level   (VARCHAR)
  - author          (VARCHAR)
  - created_at      (TIMESTAMPTZ)
```

---

### Table: `documents`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `UUID` | PK, default `gen_random_uuid()` | |
| `title` | `VARCHAR(500)` | NOT NULL | |
| `content` | `TEXT` | NOT NULL | Original / current document body |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | Updated on each save |

---

### Table: `document_versions`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `UUID` | PK, default `gen_random_uuid()` | |
| `document_id` | `UUID` | FK → `documents.id`, NOT NULL | |
| `version_number` | `INTEGER` | NOT NULL | Auto-incremented per document (max + 1) |
| `content` | `TEXT` | NOT NULL | Rewritten text |
| `reading_level` | `VARCHAR(100)` | NOT NULL | e.g., "Plain (Grades 6–8)" |
| `author` | `VARCHAR(255)` | NOT NULL | ContentDesigner identifier |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Unique constraint:** `(document_id, version_number)` — enforces append-only versioning (A3).

---

### Seed Data (for acceptance tests)

| Seed ID | Table | Data | Used by |
|---|---|---|---|
| SEED-DOC1 | `documents` | `id`: fixed UUID, `title`: "Photosynthesis", `content`: Gherkin Background text | All scenarios via Background |
| SEED-VER1 | `document_versions` | Version 1 of SEED-DOC1 (initial content, reading_level: "Original") | S13 (2 existing versions), S14, S15 |
| SEED-VER2 | `document_versions` | Version 2 of SEED-DOC1 (alternate content) | S13 (2 existing versions) |

---

### Reset Rules

| When | Action |
|---|---|
| Before each scenario | Truncate `document_versions`, then truncate `documents`; re-insert scenario-specific seeds. |
| After all scenarios | Drop test database or truncate all tables. |
