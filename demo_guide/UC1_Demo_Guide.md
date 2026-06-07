# UC1 Demo Guide — RewriteTextToReadingLevel

## Overview

This guide walks you through a live demo of **Use Case 1: Rewrite Text to Reading Level**. It covers the full user workflow, real-time AI rewriting, and database verification — all through the browser GUI.

---

## Prerequisites

| Requirement | Check |
|---|---|
| PostgreSQL running locally | `pg_isready` should show "accepting connections" |
| Anthropic API key set in `.env` | `ANTHROPIC_API_KEY=sk-ant-...` |
| Backend server running | `cd server && source .venv/bin/activate && uvicorn main:app --reload --port 8000` |
| Frontend dev server running | `cd client && npm run dev` |

**Quick start (2 terminals):**

```bash
# Terminal 1 — Backend
cd server && source .venv/bin/activate && uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd client && npm run dev
```

Then open **http://localhost:5173** in your browser.

---

## App Navigation

The app has **two tabs** at the top:

| Tab | Purpose |
|---|---|
| ✏️ **Rewrite** | Main UC1 interface — rewrite text to different reading levels |
| 🗄️ **Database** | Live database viewer — verify data in `documents` and `document_versions` tables |

---

## Demo Script

### Step 1 — Show the Database (Before)

1. Click the **🗄️ Database** tab
2. Point out:
   - **1 document** exists ("Photosynthesis") — this is the pre-seeded source document
   - **0 versions** — no rewrites have been saved yet
   - The stats bar shows **1 Document, 0 Total Versions, 2 Tables**
3. Click the document row to expand/collapse the version details

> **Talking point:** "The database starts with one source document and no saved versions."

---

### Step 2 — Rewrite to "Plain" Level

1. Switch to the **✏️ Rewrite** tab
2. The source text area shows the photosynthesis paragraph (complex, academic language)
3. Select **"Plain (Grades 6–8)"** from the dropdown
4. Click the green **Rewrite** button
5. Wait 2–3 seconds for Claude's response
6. Point out:
   - **Side-by-side view** appears: Original on the left, Rewritten on the right
   - **Grade badge** shows the measured Flesch-Kincaid grade (should be ~6–8)
   - The rewritten text uses simpler words while preserving the science content

> **Talking point:** "The system calls Claude AI in real-time and measures the actual reading grade using the Flesch-Kincaid algorithm."

---

### Step 3 — Save the Draft

1. Click the blue **Save Draft** button
2. A **green success toast** appears: "Draft saved as version 1."
3. The side-by-side view clears — the system returns to idle state

> **Talking point:** "The rewritten draft is now persisted as a new version in PostgreSQL."

---

### Step 4 — Verify in Database (After First Save)

1. Switch to the **🗄️ Database** tab
2. Click **⟳ Refresh** to reload
3. Observe:
   - Stats bar now shows **1 Total Version**
   - Expand the document row — a version table appears
   - **v1** shows:
     - `reading_level`: "Plain (Grades 6–8)"
     - `author`: "ContentDesigner"
     - `content`: the rewritten text
     - `created_at`: timestamp of when you saved it

> **Talking point:** "Version 1 is stored with full metadata — reading level, author, content, and timestamp."

---

### Step 5 — Rewrite to a Different Level

1. Switch back to **✏️ Rewrite** tab
2. Select **"Simple (Grades 4–5)"** from the dropdown
3. Click **Rewrite**
4. Compare: the new rewrite should use even simpler language than the Plain version
5. Click **Save Draft** → "Draft saved as version 2."

---

### Step 6 — Verify Append-Only Versioning

1. Switch to **🗄️ Database** tab → click **⟳ Refresh**
2. The document now shows **2 versions**:
   - **v1**: Plain (Grades 6–8) — content unchanged from Step 3
   - **v2**: Simple (Grades 4–5) — the new simpler text
3. Point out: **v1's content and timestamp have NOT changed** — this demonstrates append-only versioning

> **Talking point:** "Previous versions are immutable. Each save appends a new version without modifying existing ones."

---

### Step 7 — Demonstrate Discard

1. Switch to **✏️ Rewrite** tab
2. Select **"Very Simple (Grades 1–3)"**
3. Click **Rewrite** → see the very simple output
4. Click **Discard** instead of Save
5. Switch to **🗄️ Database** tab → **⟳ Refresh**
6. Confirm: still only **2 versions** — the discarded draft was NOT saved

> **Talking point:** "The user has full control — they can review and discard before committing to the database."

---

### Step 8 — Show All 5 Reading Levels (Optional)

Repeat the rewrite with each level to show how Claude adapts:

| Level | Expected Behavior |
|---|---|
| **Very Simple (Grades 1–3)** | Short sentences, basic words |
| **Simple (Grades 4–5)** | Slightly longer, simple vocabulary |
| **Plain (Grades 6–8)** | General public, clear explanations |
| **Standard (Grades 9–12)** | High school level, more detail |
| **Technical (Grade 13+)** | Expert vocabulary, complex sentences |

---

### Step 9 — Show Validation (Error Handling)

1. **Empty text:** Clear the source text area → the **Rewrite** button becomes disabled
2. **No reading level:** Put text back but leave the dropdown on "Choose a level…" → button stays disabled
3. These match Gherkin scenarios **S05–S08** (validation guards)

> **Talking point:** "The system validates inputs both on the client and server side, preventing invalid requests."

---

## Database Schema Reference

Show this during the database tab walkthrough:

### `documents` table
| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `title` | VARCHAR(500) | Document title |
| `content` | TEXT | Source text |
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

**Constraints:**
- `UNIQUE(document_id, version_number)` — prevents duplicate version numbers
- `FK document_id → documents(id) ON DELETE CASCADE`

---

## Architecture Summary (For Q&A)

```
Browser (React + Vite)          FastAPI Server                    Claude AI
┌──────────────────┐           ┌─────────────────────┐          ┌──────────┐
│ ✏️ RewritePage    │──POST──→ │ /api/rewrite         │──API──→ │ Anthropic│
│ 🗄️ DatabaseViewer │──GET───→ │ /api/documents/...   │          │ Claude   │
└──────────────────┘           │                     │          └──────────┘
                               │ RewriteService      │
                               │  └─ StyleRewriterPort│
                               └────────┬────────────┘
                                        │
                                   PostgreSQL
                               (documents + versions)
```

**Key design decisions:**
- **Adapter pattern**: `StyleRewriterPort` interface allows swapping between real Claude (demo) and FakeStyleRewriter (tests)
- **Append-only versioning**: Unique constraint on `(document_id, version_number)` ensures immutability
- **Flesch-Kincaid measurement**: `textstat` library measures actual reading grade of the AI output

---

## Troubleshooting

| Issue | Fix |
|---|---|
| "Failed to fetch" error | Check backend is running: `curl http://localhost:8000/api/health` |
| Rewrite button disabled | Ensure text is in the textarea AND a reading level is selected |
| Slow rewrite (~5s) | Normal — Claude API network latency |
| Database tab shows 0 docs | Click **⟳ Refresh** or re-seed: see below |

**Re-seed the demo document:**
```sql
psql -d accessibility_rewriter -c "
INSERT INTO documents (id, title, content) 
VALUES ('11111111-1111-1111-1111-111111111111', 'Photosynthesis',
'Photosynthesis is the biochemical process by which chloroplasts in plant cells convert light energy into adenosine triphosphate, facilitating the synthesis of glucose from carbon dioxide and water.')
ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content;"
```

**Reset all versions (start fresh):**
```sql
psql -d accessibility_rewriter -c "DELETE FROM document_versions;"
```
