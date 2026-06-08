# UC2 Demo Guide — MeasureReadingLevel

## Overview

This guide walks you through a live demo of **Use Case 2: Measure Reading Level**. It covers real-time Flesch-Kincaid readability analysis, the detailed breakdown with highlighted complex words and long sentences, and database verification proving UC2 is purely transient (no data is persisted).

---

## Prerequisites

| Requirement | Check |
|---|---|
| PostgreSQL running locally | `pg_isready` should show "accepting connections" |
| Backend server running | `cd server && source .venv/bin/activate && uvicorn main:app --reload --port 8000` |
| Frontend dev server running | `cd client && npm run dev` |

> **Note:** UC2 does NOT require an Anthropic API key. The readability analysis is purely algorithmic (no AI calls).

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

The app has **three tabs** at the top:

| Tab | Purpose |
|---|---|
| ✏️ **Rewrite** | UC1 — Rewrite text to different reading levels |
| 📊 **Analyze** | UC2 — Measure readability and see detailed breakdown |
| 🗄️ **Database** | Live database viewer — verify tables and data |

---

## Demo Script

### Step 1 — Show the Database (Before)

1. Click the **🗄️ Database** tab
2. Note the current state:
   - The **stats bar** shows the current number of documents and versions
   - **Write down** or remember the total version count (e.g., "2 Total Versions")
3. This baseline will be used later to prove UC2 does not write to the database

> **Talking point:** "Before we start, let's note the current database state. UC2 should NOT add any rows."

---

### Step 2 — Open the Analyze Page

1. Click the **📊 Analyze** tab
2. Point out the pre-loaded photosynthesis text in the editor:
   > *"Photosynthesis is the biochemical process by which chloroplasts in plant cells convert light energy into adenosine triphosphate..."*
3. Below the editor, an **empty state** message reads: "Select text to measure reading level"
4. The **📊 Analyze** button is ready to click

> **Talking point:** "The Analyze page lets users paste or type any text and instantly measure its readability."

---

### Step 3 — Analyze the Text (Happy Path)

1. Click the green **📊 Analyze** button
2. A **readability badge** appears instantly showing:
   - **Level name**: e.g., "Technical (Grade 13+)" — displayed in gradient text
   - **Grade number**: e.g., "Grade 15.32" — in a purple pill
   - **Stats**: word count, sentence count, average words/sentence
3. Point out how fast the badge appeared (< 200ms — no network call needed)

> **Talking point:** "The Flesch-Kincaid grade is computed client-side in under 1 millisecond. No AI or server call is needed — this is pure math."

---

### Step 4 — Open the Detailed Breakdown

1. Click the **Show Details** button on the badge
2. A **breakdown panel** expands showing:
   - **Header**: Repeats the level name and grade
   - **Legend**: Color key for word vs. sentence highlights
   - **Highlighted text**:
     - **Orange/amber underlined words** = Complex words (≥ 3 syllables) — e.g., *Photosynthesis*, *biochemical*, *chloroplasts*, *adenosine*
     - **Blue-left-bordered sentences** = Long sentences (above average word count)
   - **Complex Words list**: Chips showing each word + syllable count (e.g., "Photosynthesis (5 syl)")
3. Hover over a highlighted word to see its syllable count in the tooltip

> **Talking point:** "The breakdown identifies exactly which words and sentences make the text complex. This helps writers pinpoint what to simplify."

---

### Step 5 — Collapse the Breakdown

1. Click the **Hide Details** button
2. The breakdown panel closes
3. The **readability badge remains visible** — the grade and level name are still shown

> **Talking point:** "The toggle lets users quickly check the score and drill into details only when needed."

---

### Step 6 — Change Text and Re-Analyze

1. Clear the textarea and type a simple sentence:
   > `The cat sat on the mat. The dog ran fast.`
2. Click **📊 Analyze**
3. Observe the badge now shows a much lower grade:
   - **Level name**: e.g., "Very Simple (Grades 1–3)" or "Simple (Grades 4–5)"
   - **Grade number**: e.g., "Grade 0.9"
4. Click **Show Details** — no complex words should be highlighted (all words are 1–2 syllables)

> **Talking point:** "The score updates instantly. Simple text gets a low grade, confirming the algorithm works correctly across the full range."

---

### Step 7 — Test Edge Cases (Validation)

1. **Empty text:**
   - Clear all text from the editor
   - The **Analyze button becomes disabled**
   - The panel shows: "Select text to measure reading level"

2. **Single word:**
   - Type just `Photosynthesis`
   - Click **📊 Analyze**
   - A **yellow warning** appears: "⚠️ Selection too short for meaningful analysis"
   - No badge is shown

3. **Whitespace only:**
   - Type `   ` (spaces/tabs)
   - The **Analyze button stays disabled**

> **Talking point:** "The system gracefully handles edge cases — empty input, single words, and whitespace all produce appropriate user feedback."

---

### Step 8 — Verify the Database (After — No Writes!)

1. Switch to the **🗄️ Database** tab
2. Click **⟳ Refresh**
3. Compare the stats with your baseline from Step 1:
   - **Document count**: unchanged
   - **Total version count**: unchanged — still the same number as before
4. Expand the document row — **no new versions** have been added

> **Talking point:** "Despite running multiple analyses, the database is completely untouched. UC2 is a transient, read-only operation — no data is persisted."

---

### Step 9 — Verify the Backend API (Optional, for Technical Audiences)

Open a terminal and test the backend endpoint directly:

**Valid text:**
```bash
curl -s -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Photosynthesis is the biochemical process by which chloroplasts convert light energy."}' \
  | python3 -m json.tool
```

Expected response (200):
```json
{
    "grade": 15.73,
    "level_name": "Technical (Grade 13+)",
    "complex_words": [
        { "word": "Photosynthesis", "syllables": 5 },
        { "word": "biochemical", "syllables": 4 },
        { "word": "chloroplasts", "syllables": 3 },
        { "word": "energy", "syllables": 3 }
    ],
    "long_sentences": [],
    "average_sentence_length": 12.0,
    "total_words": 12,
    "total_sentences": 1
}
```

**Short text (should fail):**
```bash
curl -s -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello"}' \
  | python3 -m json.tool
```

Expected response (422):
```json
{
    "detail": "Selection too short for meaningful analysis"
}
```

> **Talking point:** "The same readability logic is available as a REST API for integration with other systems."

---

### Step 10 — Run Acceptance Tests (Optional, for Technical Audiences)

Run all 19 UC2 acceptance tests to prove the implementation meets the Gherkin contract:

```bash
# Make sure both servers are running, then:
cd tests/acceptance && \
source ../../server/.venv/bin/activate && \
PYTHONPATH=../../server:$(cd ../.. && pwd) \
behave features/UC2_measure_reading_level.feature --no-capture -D UC2=true
```

Expected output:
```
1 feature passed, 0 failed, 0 skipped
19 scenarios passed, 0 failed, 0 skipped
88 steps passed, 0 failed, 0 skipped
```

---

## Reading Level Taxonomy

| Grade Range | Level Name | Example Text |
|---|---|---|
| g ≤ 3 | Very Simple (Grades 1–3) | "The cat sat on the mat." |
| 3 < g ≤ 5 | Simple (Grades 4–5) | "Plants use sunlight to make food." |
| 5 < g ≤ 8 | Plain (Grades 6–8) | "Plants convert sunlight into energy through photosynthesis." |
| 8 < g ≤ 12 | Standard (Grades 9–12) | "Photosynthesis converts solar radiation into chemical energy." |
| g > 12 | Technical (Grade 13+) | "Chloroplasts facilitate adenosine triphosphate synthesis via electron transfer." |

---

## Architecture Summary (For Q&A)

```
Browser (React + Vite)            FastAPI Server
┌──────────────────────┐         ┌──────────────────────┐
│ 📊 AnalyzePage        │         │ POST /api/analyze     │
│                      │         │                      │
│ ReadabilityService   │         │ textstat (Python)    │
│ (client-side JS)     │         │ (server-side mirror) │
│  └─ fleschKincaidGrade│        └──────────────────────┘
│  └─ getComplexWords   │
│  └─ getLongSentences  │                    │
└──────────────────────┘                     │
         │                              PostgreSQL
         │                         (NOT written to by UC2)
    No network call needed
    (all computation is local)
```

**Key design decisions:**
- **Client-side computation**: Flesch-Kincaid runs in the browser (< 1ms) — no server roundtrip needed for the UI
- **Server-side mirror**: `POST /api/analyze` mirrors the logic using Python `textstat` for API consumers
- **No persistence**: UC2 is transient — the database is read-only during analysis
- **No AI dependency**: Unlike UC1, UC2 uses only algorithmic readability formulas

---

## Comparison: UC1 vs UC2

| Aspect | UC1 (Rewrite) | UC2 (Analyze) |
|---|---|---|
| **Purpose** | Transform text to target level | Measure current readability |
| **AI Required** | ✅ Claude API | ❌ Algorithmic only |
| **Network Call** | Yes (2–5s) | No (< 1ms) |
| **Database Writes** | Yes (saves versions) | No (transient) |
| **Tab** | ✏️ Rewrite | 📊 Analyze |

---

## Troubleshooting

| Issue | Fix |
|---|---|
| Analyze button disabled | Ensure text is in the editor (not empty/whitespace) |
| Badge doesn't appear | Check browser console for JS errors |
| Backend API returns 500 | Check backend is running: `curl http://localhost:8000/api/health` |
| "📊 Analyze" tab missing | Ensure frontend was restarted after the UC2 code was added |

**Shut down servers when done:**
```bash
# Find and kill processes
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:5173 | xargs kill -9  # Frontend
```
