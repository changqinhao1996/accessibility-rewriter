# UC2 — Database Design Summary: MeasureReadingLevel

## No New Tables

UC2 is a **transient, real-time analysis** (Assumption A6). No readability data is persisted to the database.

---

## Existing Tables Used

| Table | Usage in UC2 |
|---|---|
| `documents` | Source of the text to display in the editor (same as UC1 — PRE-1) |
| `document_versions` | Not written to; row count is snapshotted to verify S12 (no-persistence invariant) |

---

## Seed Data

Same as UC1 — the Background step loads a document with the photosynthesis passage. The seed document from UC1 (`id = 11111111-...`) is reused.

---

## Reset Rules

| Reset Action | When |
|---|---|
| No DB reset needed for UC2 | UC2 does not modify the database |
| Row-count snapshot before/after | Taken in S12 to assert zero change |

---

## Schema Reference (Unchanged from UC1)

### `documents` table

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `title` | VARCHAR(500) | Document title |
| `content` | TEXT | Source text displayed in the editor |
| `created_at` | TIMESTAMP | When the document was created |
| `updated_at` | TIMESTAMP | Last update time |

### `document_versions` table

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `document_id` | UUID | FK → documents.id |
| `version_number` | INTEGER | Auto-incrementing per document |
| `content` | TEXT | Rewritten text |
| `reading_level` | VARCHAR(100) | Target reading level label |
| `author` | VARCHAR(255) | Who created this version |
| `created_at` | TIMESTAMP | When the version was saved |

> **Note:** UC2 never writes to either table. The schema is listed here for reference only, since S12 asserts that row counts remain unchanged.
