# UC3 — Database Design Summary: GenerateImageAltText

## New Table: `images`

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | UUID | NO | `gen_random_uuid()` | Primary key |
| `document_id` | UUID | NO | — | FK → `documents.id` |
| `filename` | VARCHAR(500) | NO | — | Original filename |
| `file_path` | TEXT | NO | — | Server-side storage path or URL |
| `mime_type` | VARCHAR(100) | NO | — | e.g., `image/png`, `image/jpeg` |
| `alt_text` | TEXT | YES | NULL | Approved alt-text description |
| `alt_text_status` | VARCHAR(20) | NO | `'missing'` | One of: `missing`, `pending`, `described` |
| `purpose_note` | TEXT | YES | NULL | Optional user-provided context note |
| `created_at` | TIMESTAMP | NO | `now()` | When the image was added |
| `updated_at` | TIMESTAMP | NO | `now()` | Last modification time |

---

## Constraints

- `FK document_id → documents(id) ON DELETE CASCADE`
- `CHECK alt_text_status IN ('missing', 'pending', 'described')`

---

## Status Transitions

```
missing → pending    (Generate clicked)
pending → described  (Approve clicked)
pending → missing    (Cancel clicked)
missing → described  (Manual approve for complex images)
```

---

## Seed Data

| Image | Filename | Alt Text | Status | Purpose |
|---|---|---|---|---|
| Red apple photo | `apple.jpg` | NULL | `missing` | Used in S22 (hallucination check) |
| Complex infographic | `infographic.png` | NULL | `missing` | Used in S09, S15, S19 (too complex) |
| Bar chart | `barchart.png` | NULL | `missing` | Used in S24 (purpose note relevance) |
| Simple landscape | `landscape.jpg` | NULL | `missing` | Used in S01, S03–S07 (happy path) |
| Pre-described image | `described.jpg` | "A sunset over the ocean" | `described` | Used in S12 (all described) |

---

## Reset Rules

| Reset Action | When |
|---|---|
| Delete all `images` rows | Before each scenario |
| Re-seed scenario-specific images | Before each scenario based on tags |
| Reset `alt_text` to NULL and status to `missing` | Before generation scenarios |

---

## Existing Tables Used

| Table | Usage in UC3 |
|---|---|
| `documents` | Parent entity — each image belongs to a document (FK) |
| `document_versions` | Not used by UC3 |

---

## Schema Reference (Existing — Unchanged)

### `documents` table

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `title` | VARCHAR(500) | Document title |
| `content` | TEXT | Source text |
| `created_at` | TIMESTAMP | When the document was created |
| `updated_at` | TIMESTAMP | Last update time |
