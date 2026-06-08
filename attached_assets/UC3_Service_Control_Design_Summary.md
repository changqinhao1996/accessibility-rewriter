# UC3 — Service / Control Design Summary: GenerateImageAltText

## Key Design Decision: Server-Side AI Vision

Unlike UC2 (client-side computation), UC3 **requires a server-side AI call** because Claude's vision API needs the image as a base64 payload. The server acts as the intermediary.

---

## Service: `AltTextService` (Python — server-side)

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

---

## Port: `VisionAnalyzerPort` (Interface)

```python
class VisionAnalyzerPort(ABC):
    @abstractmethod
    async def analyze_image(
        self, image_data: bytes, mime_type: str, purpose_note: str | None
    ) -> VisionResult:
        """Analyze image and return alt text + complexity flag."""
        ...
```

---

## Adapters

| Adapter | When Used | Behavior |
|---|---|---|
| `AnthropicVisionAnalyzer` | Production / Demo | Calls Claude vision API with WCAG-compliant prompt |
| `FakeVisionAnalyzer` | Tests | Returns canned alt text; can simulate "too complex" and outage |

---

## Types

```python
@dataclass
class VisionResult:
    alt_text: str          # Generated alt text (≤ 125 chars)
    is_too_complex: bool   # True if image can't be described confidently
    confidence: float      # 0.0–1.0 confidence score
```

---

## API Endpoints

| Method | Path | Purpose | Response |
|---|---|---|---|
| `POST` | `/api/images/upload` | Upload image to document | 201: `{ id, filename, status }` |
| `GET` | `/api/images` | List all images with statuses | 200: `[{ id, filename, alt_text, status, ... }]` |
| `POST` | `/api/images/{id}/generate` | Generate alt text | 200: `{ alt_text, is_too_complex }` or 503 |
| `PUT` | `/api/images/{id}/approve` | Approve alt text | 200: `{ id, alt_text, status: "described" }` |
| `PUT` | `/api/images/{id}/cancel` | Cancel / discard | 200: `{ id, status: "missing" }` |

---

## External Dependencies

| Dependency | UC3 Usage |
|---|---|
| `anthropic` (Python) | Claude vision API with `claude-sonnet-4-6` model |
| Image storage | Local filesystem `uploads/` directory |
| **VisionAnalyzerPort** | Adapter pattern (same as UC1's StyleRewriterPort) |

---

## WCAG Prompt Template

The system prompt sent to Claude for alt text generation:

```
You are a WCAG 2.1 accessibility expert. Generate alt text for the provided image.

Rules:
- Describe ONLY what is visible in the image — never invent or assume elements
- Keep the description concise: at most 125 characters
- Do NOT start with "image of", "picture of", "photo of", or similar prefixes
- Be specific and descriptive
- If the image is too complex (dense charts, infographics with many data points), 
  respond with: {"alt_text": "", "is_too_complex": true}

If a purpose note is provided, use it to give context-appropriate descriptions.

Respond in JSON: {"alt_text": "...", "is_too_complex": false}
```

---

## Integration with UC1 / UC2

| Aspect | How UC3 Integrates |
|---|---|
| Shared `documents` table | Images FK to `documents.id` — same parent entity |
| Shared adapter pattern | `VisionAnalyzerPort` mirrors `StyleRewriterPort` from UC1 |
| Shared `anthropic` dependency | Same API key, same client library |
| Independent page | 🖼️ Alt Text tab is separate from ✏️ Rewrite and 📊 Analyze |
| No dependency on UC1/UC2 | UC3 does not call rewrite or analyze endpoints |
