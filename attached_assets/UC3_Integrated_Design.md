# UC3 — GenerateImageAltText: Integrated Design

---

## A) UI Design Summary

### Page / Component: AltTextPage

UC3 adds a new **🖼️ Alt Text** tab to the application. This is a dedicated page where the ContentDesigner uploads/selects images and generates WCAG-compliant alt-text descriptions.

### Component Hierarchy

```
AltTextPage (new — UC3)
├── ImageUploadArea              — Drop zone + file picker for uploading images
│   └── ImagePreview             — Thumbnail preview of selected image
├── PurposeNoteInput             — Optional textarea for context note
├── GenerateButton               — "Generate Alt Text" action
├── AltTextReviewPanel           — Review/edit area for generated text
│   ├── AltTextDisplay           — Editable textarea showing generated alt text
│   ├── CharacterCounter         — Shows length vs 125-char WCAG limit
│   ├── ApproveButton            — Confirm and save
│   ├── RegenerateButton         — Request a new generation
│   └── CancelButton             — Discard without saving
├── ManualInputPanel             — Shown when image is flagged as too complex
│   ├── ComplexWarning           — Warning banner explaining why
│   └── ManualAltTextInput       — Textarea for hand-written alt text
├── ImageGallery                 — Grid of all images in the document
│   ├── ImageCard                — Each image with status badge
│   │   ├── DescribedBadge       — ✅ green badge when alt text exists
│   │   └── MissingBadge         — ⚠️ orange badge when no alt text
│   └── AllDescribedMessage      — "All images are described" banner
├── EmptyState                   — "No images found in this document"
└── ErrorBanner                  — Error message + Retry button
```

### UI Elements Inventory

| Element ID | Type | Visible When | Content / Behavior |
|---|---|---|---|
| `alttext-page` | Container | Always | Page wrapper |
| `image-upload` | Drop zone + file input | Always | Accepts JPEG, PNG, GIF, WebP |
| `image-preview` | `<img>` | Image selected/uploaded | Thumbnail of selected image |
| `purpose-note` | Textarea | Image selected | Optional context note (placeholder: "Describe the image's purpose…") |
| `generate-btn` | Button | Image selected | "🖼️ Generate Alt Text" — disabled if no image |
| `alttext-review` | Container | Alt text generated | Review panel wrapper |
| `alttext-textarea` | Editable textarea | Alt text generated | Shows generated text; user can edit |
| `char-counter` | Span | Alt text generated | "42 / 125 characters" — turns red if > 125 |
| `approve-btn` | Button | Alt text in review area | "✅ Approve" — saves to database |
| `regenerate-btn` | Button | Alt text in review area | "🔄 Regenerate" — requests new generation |
| `cancel-btn` | Button | Alt text in review area | "Cancel" — discards without saving |
| `manual-input-panel` | Container | Image flagged as too complex | Manual entry area |
| `complex-warning` | Warning banner | Image flagged as too complex | "This image is too complex for automatic description. Please write alt text manually." |
| `manual-alttext` | Textarea | Image flagged as too complex | Manual alt text input |
| `image-gallery` | Grid | Always | All images with status badges |
| `image-card` | Card | Per image | Image thumbnail + described/missing badge |
| `described-badge` | Badge | Image has alt text | ✅ "Described" |
| `missing-badge` | Badge | Image lacks alt text | ⚠️ "Missing" |
| `all-described-msg` | Banner | All images have alt text | "All images are described" |
| `no-images-msg` | Banner | Document has no images | "No images found in this document" |
| `error-banner` | Banner | AI service error | Error message |
| `retry-btn` | Button | AI service error | "Retry" |
| `success-toast` | Toast | Alt text approved | "Alt text saved successfully" |
| `select-prompt` | Banner | Generate clicked without image | "Please select an image first" |

### State Machine

```
┌────────────┐  select image  ┌──────────────┐  click Generate  ┌────────────────┐
│  idle      │───────────────→│ image-ready  │──────────────────→│ generating...  │
│ (gallery   │                │ (preview +   │                   │ (loading)      │
│  shown)    │                │  note input) │                   └───────┬────────┘
└────────────┘                └──────────────┘                          │
                                                          ┌────────────┴─────────────┐
                                                          │                          │
                                                          ↓                          ↓
                                                 ┌────────────────┐        ┌─────────────────┐
                                                 │ review         │        │ too-complex      │
                                                 │ (alt text in   │        │ (manual input    │
                                                 │  editable area)│        │  shown)          │
                                                 └───┬──────┬─────┘       └────────┬─────────┘
                                                     │      │                      │
                                              Approve│  Cancel│            Approve  │
                                                     │      │                      │
                                                     ↓      ↓                      ↓
                                              ┌──────────┐ ┌──────┐         ┌──────────┐
                                              │ saved    │ │ idle │         │ saved    │
                                              │ (badge   │ │      │         │ (badge   │
                                              │  updated)│ │      │         │  updated)│
                                              └──────────┘ └──────┘         └──────────┘
```

---

## B) Database Design Summary

### New Table: `images`

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

**Constraints:**
- `FK document_id → documents(id) ON DELETE CASCADE`
- `CHECK alt_text_status IN ('missing', 'pending', 'described')`

### Status Transitions

```
missing → pending    (Generate clicked)
pending → described  (Approve clicked)
pending → missing    (Cancel clicked)
missing → described  (Manual approve for complex images)
```

### Seed Data

| Image | Filename | Alt Text | Status | Purpose |
|---|---|---|---|---|
| Red apple photo | `apple.jpg` | NULL | `missing` | Used in S22 (hallucination check) |
| Complex infographic | `infographic.png` | NULL | `missing` | Used in S09, S15, S19 (too complex) |
| Bar chart | `barchart.png` | NULL | `missing` | Used in S24 (purpose note relevance) |
| Simple landscape | `landscape.jpg` | NULL | `missing` | Used in S01, S03–S07 (happy path) |
| Pre-described image | `described.jpg` | "A sunset over the ocean" | `described` | Used in S12 (all described) |

### Reset Rules

| Reset Action | When |
|---|---|
| Delete all `images` rows | Before each scenario |
| Re-seed scenario-specific images | Before each scenario based on tags |
| Reset `alt_text` to NULL and status to `missing` | Before generation scenarios |

---

## C) Service / Control Design Summary

### Key Design Decision: Server-Side AI Vision

Unlike UC2 (client-side computation), UC3 **requires a server-side AI call** because Claude's vision API needs the image as a base64 payload. The server acts as the intermediary.

### Service: `AltTextService` (Python — server-side)

```
AltTextService
├── generate_alt_text(image_path, purpose_note?) → AltTextResult
│   ├── Load image from file_path
│   ├── Convert to base64
│   ├── Call Claude vision API with WCAG prompt
│   ├── Parse response for alt text + complexity flag
│   └── Return { alt_text, is_too_complex, confidence }
├── approve_alt_text(image_id, alt_text) → Image
│   ├── Update image record: alt_text = approved text
│   ├── Set alt_text_status = 'described'
│   └── Return updated image
└── cancel_generation(image_id) → Image
    ├── Set alt_text_status = 'missing'
    ├── Set alt_text = NULL
    └── Return updated image
```

### Port: `VisionAnalyzerPort` (Interface)

```python
class VisionAnalyzerPort(ABC):
    @abstractmethod
    async def analyze_image(
        self, image_data: bytes, mime_type: str, purpose_note: str | None
    ) -> VisionResult:
        """Analyze image and return alt text + complexity flag."""
        ...
```

### Adapters

| Adapter | When Used | Behavior |
|---|---|---|
| `AnthropicVisionAnalyzer` | Production / Demo | Calls Claude vision API with WCAG-compliant prompt |
| `FakeVisionAnalyzer` | Tests | Returns canned alt text; can simulate "too complex" and outage |

### Types

```python
@dataclass
class VisionResult:
    alt_text: str          # Generated alt text (≤ 125 chars)
    is_too_complex: bool   # True if image can't be described confidently
    confidence: float      # 0.0–1.0 confidence score
```

### API Endpoints

| Method | Path | Purpose | Response |
|---|---|---|---|
| `POST` | `/api/images/upload` | Upload image to document | 201: `{ id, filename, status }` |
| `GET` | `/api/images` | List all images with statuses | 200: `[{ id, filename, alt_text, status, ... }]` |
| `POST` | `/api/images/{id}/generate` | Generate alt text | 200: `{ alt_text, is_too_complex }` or 503 |
| `PUT` | `/api/images/{id}/approve` | Approve alt text | 200: `{ id, alt_text, status: "described" }` |
| `PUT` | `/api/images/{id}/cancel` | Cancel / discard | 200: `{ id, status: "missing" }` |

### External Dependencies

| Dependency | UC3 Usage |
|---|---|
| `anthropic` (Python) | Claude vision API with `claude-sonnet-4-6` model |
| Image storage | Local filesystem `uploads/` directory |
| **VisionAnalyzerPort** | Adapter pattern (same as UC1's StyleRewriterPort) |

---

## D) Acceptance Harness Design

### Framework

Same as UC1/UC2: **Behave** (Python) + **Playwright** for browser automation.

### Before Each Scenario

| Action | Detail |
|---|---|
| Reset `images` table | Delete all rows, re-seed based on scenario tags |
| Seed test images | Copy fixture images to `uploads/` directory |
| Configure FakeVisionAnalyzer | Set canned responses, complexity flags, or outage simulation |
| Navigate to AltText page | Open `http://localhost:5173` → click "🖼️ Alt Text" tab |

### Scenario-Specific Seeding

| Scenario Tags | Seed Data |
|---|---|
| `@happy-path` (default) | 1 image without alt text (`landscape.jpg`) |
| `UC3-S06` | 2 images without alt text |
| `UC3-S09`, `UC3-S15`, `UC3-S19` | 1 complex infographic → FakeVisionAnalyzer returns `is_too_complex: true` |
| `UC3-S10` | FakeVisionAnalyzer.simulate_outage = True |
| `UC3-S12` | 1 image with alt text already set (`described`) |
| `UC3-S14` | 0 images |
| `UC3-S22` | 1 apple image → FakeVisionAnalyzer returns "Red apple on a white table" |
| `UC3-S24` | 1 bar chart image |

### UI Actions Simulated

| Simulated Action | Playwright Mechanism |
|---|---|
| Upload/select image | `page.set_input_files('#image-upload', 'fixtures/landscape.jpg')` |
| Enter purpose note | `page.fill('#purpose-note', 'Diagram showing...')` |
| Click Generate | `page.click('#generate-btn')` |
| Edit alt text | `page.fill('#alttext-textarea', 'Custom text')` |
| Click Approve | `page.click('#approve-btn')` |
| Click Regenerate | `page.click('#regenerate-btn')` |
| Click Cancel | `page.click('#cancel-btn')` |
| Click Retry | `page.click('#retry-btn')` |
| Type manual alt text | `page.fill('#manual-alttext', 'Manual description')` |

### DB State Asserted

| Assertion | How |
|---|---|
| Alt text saved | `SELECT alt_text FROM images WHERE id = ?` = approved text |
| Status is "described" | `SELECT alt_text_status FROM images WHERE id = ?` = `'described'` |
| Alt text is NULL after cancel | `SELECT alt_text FROM images WHERE id = ?` IS NULL |
| Status unchanged after cancel | `SELECT alt_text_status FROM images WHERE id = ?` = `'missing'` |
| Edited text persisted (not AI original) | `SELECT alt_text` matches user edit, not canned response |

### Metrics Recorded

| Metric | How | Used By |
|---|---|---|
| Generation latency | `time.time()` before Generate → after result appears | S23 |
| Alt text character count | `len(alt_text)` | S20 |
| Alt text prefix check | `alt_text.lower().startswith(...)` | S21 |
| Content faithfulness | Compare against known image content | S22 |

### Step Definition Mapping

```
steps/uc3_steps.py
├── @given("the ContentDesigner has loaded a document ...")    → DB seed + navigate
├── @given("the ContentDesigner has generated alt text ...")   → Upload + Generate flow
├── @given("the document contains two images ...")             → Seed 2 images
├── @given("the AI vision service is unavailable")             → FakeVisionAnalyzer.outage
├── @given("the system has flagged an image as too complex")   → FakeVisionAnalyzer.complex
├── @when("the ContentDesigner selects an image ...")          → File input
├── @when('the ContentDesigner clicks "Generate Alt Text"')    → Button click
├── @when('the ContentDesigner clicks "Approve"')              → Button click
├── @when('the ContentDesigner clicks "Regenerate"')           → Button click
├── @when('the ContentDesigner clicks "Cancel"')               → Button click
├── @when("the ContentDesigner edits the alt text to ...")     → Fill textarea
├── @when("the ContentDesigner enters the purpose note ...")   → Fill purpose note
├── @then("the system displays a generated alt-text ...")      → Assert textarea visible
├── @then("the generated alt text is non-empty")               → Assert len > 0
├── @then('the image is marked as "described"')                → Assert badge visible
├── @then("the database record for the image contains ...")    → DB query
├── @then("the generated alt text is at most 125 characters")  → Assert len ≤ 125
├── @then('does not start with "image of"')                    → Assert prefix
├── @then("the generated alt text appears within 10 seconds")  → Timing check
└── @then('the system shows a message: "..."')                 → Assert banner text
```

---

## E) Traceability Table

| Scenario ID | Category | UI Elements | DB Elements | Service Elements |
|---|---|---|---|---|
| UC3-S01 | Happy path | `image-upload`, `generate-btn`, `alttext-textarea` | — | `VisionAnalyzerPort.analyze_image()` |
| UC3-S02 | Happy path | `purpose-note`, `generate-btn`, `alttext-textarea` | — | `analyze_image(note=...)` |
| UC3-S03 | Happy path | `approve-btn`, `described-badge`, `success-toast` | `alt_text` SET, `status='described'` | `AltTextService.approve_alt_text()` |
| UC3-S04 | Happy path | `alttext-textarea` (edit), `approve-btn` | `alt_text` = edited text | `approve_alt_text(edited)` |
| UC3-S05 | Happy path | `regenerate-btn`, `alttext-textarea` (new) | — | `analyze_image()` ×2 |
| UC3-S06 | Happy path | `image-card` ×2, `described-badge` ×2 | 2 rows `status='described'` | `approve_alt_text()` ×2 |
| UC3-S07 | Happy path | `described-badge` | `status='described'` | — |
| UC3-S08 | Negative | `select-prompt`, `generate-btn` (disabled) | — | — (validation) |
| UC3-S09 | Negative | `complex-warning`, `manual-input-panel`, `manual-alttext` | — | `analyze_image()` → `is_too_complex` |
| UC3-S10 | Negative | `error-banner`, `retry-btn` | — | `analyze_image()` → exception |
| UC3-S11 | Negative | `cancel-btn` | `alt_text` NULL, `status='missing'` | `cancel_generation()` |
| UC3-S12 | Negative | `all-described-msg` | All rows `status='described'` | — |
| UC3-S13 | Negative | `purpose-note` (empty), `alttext-textarea` | — | `analyze_image(note=None)` |
| UC3-S14 | Negative | `no-images-msg` | 0 image rows | — |
| UC3-S15 | Negative | `manual-alttext`, `approve-btn` | `alt_text` = manual text, `status='described'` | `approve_alt_text(manual)` |
| UC3-S16 | Persistence | `approve-btn` | `alt_text` SET, `status='described'` | `approve_alt_text()` |
| UC3-S17 | Persistence | `alttext-textarea` (edit), `approve-btn` | `alt_text` = edited (not AI) | `approve_alt_text(edited)` |
| UC3-S18 | Persistence | `cancel-btn` | `alt_text` NULL, `status` unchanged | `cancel_generation()` |
| UC3-S19 | Persistence | `manual-alttext`, `approve-btn` | `alt_text` = manual, `status='described'` | `approve_alt_text(manual)` |
| UC3-S20 | Quality | `alttext-textarea`, `char-counter` | — | `analyze_image()` + `len()` ≤ 125 |
| UC3-S21 | Quality | `alttext-textarea` | — | `analyze_image()` + prefix check |
| UC3-S22 | Quality | `alttext-textarea` | — | `analyze_image()` + content check |
| UC3-S23 | Quality | `alttext-textarea` (timing) | — | `analyze_image()` + `time.time()` ≤ 10s |
| UC3-S24 | Quality | `purpose-note`, `alttext-textarea` | — | `analyze_image(note=...)` + relevance |
| UC3-S25 | Quality | `regenerate-btn`, `alttext-textarea` | — | `analyze_image()` ×2, compare |
