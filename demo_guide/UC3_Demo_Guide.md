# UC3 Demo Guide — GenerateImageAltText

## Overview

This guide walks you through a live demo of **Use Case 3: Generate Image Alt Text**. It covers uploading images, generating WCAG-compliant alt text via AI vision, reviewing and editing descriptions, handling complex images, and database verification proving alt text is persisted correctly.

---

## Prerequisites

| Requirement | Check |
|---|---|
| PostgreSQL running locally | `pg_isready` should show "accepting connections" |
| Backend server running (fake mode) | `cd server && source .venv/bin/activate && USE_FAKE_REWRITER=true uvicorn main:app --reload --port 8000` |
| Frontend dev server running | `cd client && npm run dev` |

> **Note:** For demo purposes, the backend uses `USE_FAKE_REWRITER=true` to enable the FakeVisionAnalyzer, which returns canned alt text without needing an Anthropic API key. For production, remove this flag and set `ANTHROPIC_API_KEY` in `.env` to use Claude Vision.

**Quick start (2 terminals):**

```bash
# Terminal 1 — Backend (with fake adapter for demo)
cd server && source .venv/bin/activate && USE_FAKE_REWRITER=true uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd client && npm run dev
```

Then open **http://localhost:5173** in your browser.

---

## App Navigation

The app has **four tabs** at the top:

| Tab | Purpose |
|---|---|
| ✏️ **Rewrite** | UC1 — Rewrite text to different reading levels |
| 📊 **Analyze** | UC2 — Measure readability and see detailed breakdown |
| 🖼️ **Alt Text** | UC3 — Generate WCAG-compliant alt text for images |
| 🗄️ **Database** | Live database viewer — verify tables and data |

---

## Demo Script

### Step 1 — Show the Database (Before)

1. Click the **🗄️ Database** tab
2. Note the current state of the **images table**:
   - If no images exist yet, that's expected — we'll add some during the demo
   - If images exist from previous runs, note how many have status `described` vs `missing`
3. This baseline will be used later to prove UC3 persists alt text correctly

> **Talking point:** "Before we start, let's look at the database. UC3 stores image records with an `alt_text_status` field that tracks whether each image has been described."

---

### Step 2 — Open the Alt Text Page

1. Click the **🖼️ Alt Text** tab
2. Point out the page layout:
   - **Page header**: "Generate Image Alt Text"
   - **Upload area**: A dashed drop zone with text "Drop an image here or click to browse"
   - **Generate button**: The orange **🖼️ Generate Alt Text** button
   - **Image Gallery**: Shows previously uploaded images with status badges (✅ Described / ⚠️ Missing)

> **Talking point:** "The Alt Text page gives content designers a single workflow for uploading images, generating alt text with AI, and approving the final description."

---

### Step 3 — Upload an Image (Happy Path)

1. Click the **upload drop zone** or drag-and-drop an image
2. A **file chooser dialog** opens — select any JPEG, PNG, GIF, or WebP image
3. After upload, the drop zone changes to show:
   - **Thumbnail preview** of the uploaded image
   - **Filename** and current status
   - **✕ Remove button** to clear the selection
4. The **Purpose Note** field appears below with placeholder text

> **Talking point:** "Users can upload images by clicking or dragging. The system immediately creates a database record and displays a preview."

---

### Step 4 — Generate Alt Text Without a Purpose Note

1. Leave the **Purpose Note** empty
2. Click **🖼️ Generate Alt Text**
3. A **loading spinner** appears briefly: "Generating alt text…"
4. The **Review Panel** appears with:
   - **📝 Review Generated Alt Text** header
   - **Editable textarea** containing the AI-generated description
   - **Character counter**: e.g., "46 / 125 characters"
   - Three action buttons: **✅ Approve**, **🔄 Regenerate**, **Cancel**

> **Talking point:** "The AI generates a WCAG-compliant alt text — always under 125 characters, and it never starts with 'image of' or 'picture of'."

---

### Step 5 — Edit and Approve the Alt Text

1. In the review textarea, **edit the text** to customize it:
   > Change to: `Simplified diagram of photosynthesis`
2. Notice the **character counter** updates in real time
3. Click **✅ Approve**
4. A **green success toast** appears: "Alt text saved successfully"
5. In the **Image Gallery** below, the image now shows a **✅ Described** badge

> **Talking point:** "Users can edit the AI suggestion before approving. The system saves the final human-approved text, not the raw AI output."

---

### Step 6 — Generate Alt Text With a Purpose Note

1. Upload a **new image** (click the drop zone again)
2. In the **Purpose Note** field, type:
   > `Diagram showing the water cycle`
3. Click **🖼️ Generate Alt Text**
4. The generated alt text now **references the purpose note context** (e.g., mentions "water cycle")

> **Talking point:** "The purpose note gives the AI additional context, resulting in more relevant and accurate descriptions."

---

### Step 7 — Regenerate Alt Text

1. After generating alt text, **note the current description**
2. Click **🔄 Regenerate**
3. A new description appears — **different from the previous one**
4. The new text replaces the old one in the review area

> **Talking point:** "If the first suggestion isn't ideal, users can regenerate to get a different description without starting over."

---

### Step 8 — Cancel Without Approving

1. Generate alt text for an image
2. Click **Cancel** instead of Approve
3. The review panel closes
4. The image **remains without alt text** — no data is persisted
5. In the Image Gallery, the image still shows **⚠️ Missing**

> **Talking point:** "Canceling discards the AI suggestion completely. No data is written to the database until the user explicitly approves."

---

### Step 9 — Test Edge Cases (Validation)

#### 9a — No Image Selected

1. Make sure no image is selected (remove any current image with ✕)
2. Click **🖼️ Generate Alt Text**
3. A **blue prompt** appears: "Please select an image first"
4. No alt text is generated

#### 9b — Complex Image (Too Complex)

1. Upload an **infographic** or complex chart image
2. Click **🖼️ Generate Alt Text**
3. A **yellow warning banner** appears: "⚠️ This image is too complex for automatic description"
4. A **Manual Alt Text** input field appears
5. Type a description manually and click **✅ Approve**
6. The image is marked as **✅ Described**

> **Talking point:** "When the AI can't confidently describe a complex image, it flags it and asks the user to write alt text manually. This ensures every image gets a description."

#### 9c — AI Service Unavailable

> *(To demonstrate this, the backend must be configured to simulate an outage. This happens automatically in acceptance tests but can be triggered manually via the test endpoint.)*

1. The system shows an **error banner** with a **🔄 Retry** button
2. Clicking Retry attempts the generation again

---

### Step 10 — Verify the Database (After)

1. Switch to the **🗄️ Database** tab
2. Click **⟳ Refresh**
3. Verify the **images table** now contains:
   - Approved images have `alt_text_status = described` and a non-null `alt_text` value
   - Cancelled images still have `alt_text_status = missing` and `alt_text = NULL`
4. Expand individual rows to see the full alt text content

> **Talking point:** "The database confirms that approved alt text is persisted with the correct status. Cancelled operations leave no trace."

---

### Step 11 — Verify via pgAdmin4 (Optional)

1. Open **pgAdmin4** in your browser
2. Navigate to: Servers → PostgreSQL → Databases → `accessibility_rewriter` → Schemas → public → Tables → `images`
3. Right-click `images` → **View/Edit Data → All Rows**
4. Confirm the `alt_text` and `alt_text_status` columns match the UI

> **Talking point:** "pgAdmin4 provides an independent view of the database, confirming what the app shows is backed by real data."

---

### Step 12 — Verify the Backend API (Optional, for Technical Audiences)

**Upload an image:**
```bash
curl -s -X POST http://localhost:8000/api/images/upload \
  -F "file=@/path/to/your/image.png" \
  -F "document_id=11111111-1111-1111-1111-111111111111" \
  | python3 -m json.tool
```

Expected response (201):
```json
{
    "id": "a1b2c3d4-...",
    "document_id": "11111111-1111-1111-1111-111111111111",
    "filename": "image.png",
    "image_url": "/uploads/a1b2c3d4-....png",
    "alt_text": null,
    "alt_text_status": "missing",
    "purpose_note": null
}
```

**Generate alt text:**
```bash
curl -s -X POST http://localhost:8000/api/images/{IMAGE_ID}/generate \
  -H "Content-Type: application/json" \
  -d '{"purpose_note": "Diagram showing the water cycle"}' \
  | python3 -m json.tool
```

Expected response (200):
```json
{
    "alt_text": "Contextual description relating to Diagram showing the water cycle",
    "is_too_complex": false
}
```

**Approve alt text:**
```bash
curl -s -X PUT http://localhost:8000/api/images/{IMAGE_ID}/approve \
  -H "Content-Type: application/json" \
  -d '{"alt_text": "Water cycle diagram showing evaporation and precipitation"}' \
  | python3 -m json.tool
```

Expected response (200):
```json
{
    "id": "a1b2c3d4-...",
    "alt_text": "Water cycle diagram showing evaporation and precipitation",
    "alt_text_status": "described",
    ...
}
```

> **Talking point:** "The same image alt text workflow is available as a REST API for integration with content management systems."

---

### Step 13 — Run Acceptance Tests (Optional, for Technical Audiences)

Run all 25 UC3 acceptance tests to prove the implementation meets the Gherkin contract:

```bash
# Make sure both servers are running (backend with USE_FAKE_REWRITER=true), then:
cd tests/acceptance && \
source ../../server/.venv/bin/activate && \
PYTHONPATH=../../server:$(cd ../.. && pwd) \
behave features/UC3_generate_image_alt_text.feature --no-capture -D UC3=true
```

Expected output:
```
1 feature passed, 0 failed, 0 skipped
25 scenarios passed, 0 failed, 0 skipped
123 steps passed, 0 failed, 0 skipped
```

---

## WCAG Alt Text Rules

The system enforces these WCAG 2.1 guidelines automatically:

| Rule | Enforcement |
|---|---|
| **Max 125 characters** | Character counter turns red if exceeded |
| **No "image of" prefix** | AI is instructed to never start with "image of", "picture of", or "photo of" |
| **Descriptive content** | Alt text describes visible content — no invented elements |
| **Complex image handling** | Flagged for manual description when AI cannot describe confidently |

---

## Scenario Coverage

The 25 acceptance test scenarios cover:

| Category | Count | Scenarios | What They Test |
|---|---|---|---|
| **Happy Path** | 7 | S01–S07 | Basic generation, purpose notes, approve, edit, regenerate, multi-image, described indicator |
| **Negative** | 8 | S08–S15 | No image selected, too complex, service outage, cancel, all described, empty note, no images, manual write |
| **Persistence** | 4 | S16–S19 | Approved text persisted, edited text persisted, cancel doesn't modify DB, manual text persisted |
| **Quality/NFR** | 6 | S20–S25 | ≤125 chars, no forbidden prefixes, no hallucination, <10s performance, purpose note relevance, regeneration produces different text |

---

## Architecture Summary (For Q&A)

```
Browser (React + Vite)            FastAPI Server              AI Vision
┌──────────────────────┐         ┌──────────────────────┐    ┌──────────────┐
│ 🖼️ AltTextPage        │  POST   │ /api/images/upload   │    │ Claude Vision │
│                      │ ──────→ │ /api/images          │    │ (Anthropic)  │
│ • Upload drop zone   │         │ /api/images/:id/gen  │ →  │              │
│ • Purpose note       │         │ /api/images/:id/ok   │    │ or           │
│ • Review panel       │         │ /api/images/:id/cancel│    │              │
│ • Manual input       │         │                      │    │ Fake Adapter │
│ • Image gallery      │         │ AltTextService       │    │ (for tests)  │
└──────────────────────┘         └──────────────────────┘    └──────────────┘
                                          │
                                    PostgreSQL
                                 ┌──────────────┐
                                 │ images table  │
                                 │ • id          │
                                 │ • filename    │
                                 │ • alt_text    │
                                 │ • status      │
                                 │ • file_path   │
                                 └──────────────┘
```

**Key design decisions:**
- **Adapter pattern**: `VisionAnalyzerPort` abstracts the AI service — production uses Claude Vision, tests use `FakeVisionAnalyzer`
- **File uploads**: Images are stored on disk in `/uploads/` and served via FastAPI static files
- **Transactional state machine**: `alt_text_status` transitions: `missing` → `pending` → `described` (or back to `missing` on cancel)
- **WCAG compliance**: Alt text is capped at 125 characters, forbidden prefixes are blocked, complex images are flagged

---

## Comparison: UC1 vs UC2 vs UC3

| Aspect | UC1 (Rewrite) | UC2 (Analyze) | UC3 (Alt Text) |
|---|---|---|---|
| **Purpose** | Transform text to target level | Measure current readability | Generate image alt text |
| **AI Required** | ✅ Claude API | ❌ Algorithmic only | ✅ Claude Vision |
| **Input** | Text | Text | Image file + optional note |
| **Network Call** | Yes (2–5s) | No (<1ms) | Yes (1–3s) |
| **Database Writes** | Yes (saves versions) | No (transient) | Yes (saves alt text) |
| **Tab** | ✏️ Rewrite | 📊 Analyze | 🖼️ Alt Text |

---

## Troubleshooting

| Issue | Fix |
|---|---|
| Alt Text tab missing | Ensure frontend was restarted after the UC3 code was added |
| Upload fails | Check backend is running: `curl http://localhost:8000/api/health` |
| "AI vision service unavailable" | Ensure `USE_FAKE_REWRITER=true` is set for demo mode |
| Image gallery empty | Upload an image first — images are per-document |
| Alt text not generating | Check browser console for errors; verify backend logs |
| Character counter shows red | Alt text exceeds 125 characters — edit to shorten |
| Complex warning always shows | Backend may be in "complex" mode — restart with default settings |
| Acceptance tests fail | Ensure backend is running with `USE_FAKE_REWRITER=true` |

**Shut down servers when done:**
```bash
# Find and kill processes
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:5173 | xargs kill -9  # Frontend
```
