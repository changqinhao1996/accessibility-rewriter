# UC3 — UI Design Summary: GenerateImageAltText

## Page / Component: AltTextPage

UC3 adds a new **🖼️ Alt Text** tab to the application. This is a dedicated page where the ContentDesigner uploads/selects images and generates WCAG-compliant alt-text descriptions.

---

## Component Hierarchy

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

---

## UI Elements Inventory

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

---

## State Machine

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
