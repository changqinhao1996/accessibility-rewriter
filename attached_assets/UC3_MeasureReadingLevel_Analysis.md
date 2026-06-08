# UC3 — GenerateImageAltText: Analysis & Acceptance Tests

---

## A) Structured Requirement Specification

### Use Case Name
**GenerateImageAltText**

### Participating Actors
| Actor | Role |
|---|---|
| **ContentDesigner** | Initiator — selects an image, optionally adds a purpose note, reviews and approves the generated alt text |
| **AccessibilityChecker** | System service — analyzes the image (and optional note), generates a WCAG-compliant alt-text description |

### Goal
Enable the ContentDesigner to generate, review, and attach WCAG-compliant alt-text descriptions to images in a document, so that the document meets accessibility standards.

### Preconditions
| ID | Precondition |
|---|---|
| PRE-1 | The document contains at least one image without alt text |

### Main Success Flow
| Step | Actor | Action |
|---|---|---|
| 1 | ContentDesigner | Selects an image in the document and, optionally, adds a note describing the image's purpose |
| 2 | System (AccessibilityChecker) | Analyzes the image and the note, generates a WCAG-compliant alt-text description, and displays it for review |
| 3 | ContentDesigner | Approves the alt text |
| 4 | System | Attaches the approved alt text to the image and marks the image as described |

### Alternative / Failure Flows
| ID | Condition | Action |
|---|---|---|
| ALT-1 | Image is too complex for AI to describe accurately | System flags the image as too complex and asks the ContentDesigner to write the description manually |
| ALT-2 | ContentDesigner rejects the generated alt text | ContentDesigner can edit the alt text before approving, or regenerate |
| ALT-3 | No image selected | System shows a prompt to select an image |
| ALT-4 | AI service is unavailable | System shows an error message and allows retry |

### Success Postconditions
| ID | Postcondition |
|---|---|
| POST-1 | The image has an approved alt-text description attached |
| POST-2 | The image is marked as "described" (has alt text) |

### Failure Postconditions
| ID | Postcondition |
|---|---|
| FPOST-1 | The system flags the image as too complex and asks the ContentDesigner to write the description manually |
| FPOST-2 | No alt text is attached; the image remains in its original state |

### Quality Requirements
| ID | Requirement |
|---|---|
| QR-1 | The generated alt text describes **only** what appears in the image and never invents elements that are not present (faithfulness / no hallucination) |
| QR-2 | The generated alt text is WCAG-compliant (concise, descriptive, ≤ 125 characters recommended, avoids "image of" / "picture of" prefixes) |
| QR-3 | The alt text generation completes within a reasonable time (≤ 10 seconds) |

### Assumptions
| ID | Assumption |
|---|---|
| A1 | The system uses an AI vision model (e.g., Claude with vision) to analyze images |
| A2 | Images are uploaded/provided in standard web formats (JPEG, PNG, GIF, WebP) |
| A3 | The "too complex" determination is made by the AI service based on confidence or image type (e.g., charts, infographics with dense data) |
| A4 | "WCAG-compliant" follows WCAG 2.1 Success Criterion 1.1.1 (Non-text Content) |
| A5 | The optional purpose note is free-text and helps the AI understand the image's context (e.g., "This is a diagram showing the water cycle") |
| A6 | A document can contain multiple images; each is processed individually |
| A7 | The "mark as described" status is persisted in the database |
| A8 | The ContentDesigner can edit the generated alt text before approving |

---

## B) Acceptance Checks Table

| Check ID | Source | Acceptance Check | Type |
|---|---|---|---|
| AC-01 | Flow Step 1 | ContentDesigner can select an image from the document | UI |
| AC-02 | Flow Step 1 | ContentDesigner can optionally add a purpose note for the image | UI |
| AC-03 | Flow Step 2 | System generates a WCAG-compliant alt-text description after analyzing the image | Functional |
| AC-04 | Flow Step 2 | If a purpose note is provided, the AI uses it to improve the alt text | Functional |
| AC-05 | Flow Step 2 | The generated alt text is displayed in a review area for the ContentDesigner | UI |
| AC-06 | Flow Step 3 | ContentDesigner can approve the generated alt text | UI |
| AC-07 | Flow Step 3 | ContentDesigner can edit the alt text before approving | UI |
| AC-08 | Flow Step 3 | ContentDesigner can regenerate the alt text if unsatisfied | UI |
| AC-09 | Flow Step 3 | ContentDesigner can reject and write alt text manually | UI |
| AC-10 | Flow Step 4 | On approval, the alt text is attached to the image in the database | Persistence |
| AC-11 | Flow Step 4 | On approval, the image is marked as "described" | Persistence |
| AC-12 | ALT-1 | If the image is too complex, the system flags it and prompts manual entry | Functional |
| AC-13 | ALT-3 | If no image is selected, the system shows a prompt | UI / Validation |
| AC-14 | ALT-4 | If the AI service is unavailable, an error is shown with retry option | Error handling |
| AC-15 | PRE-1 | The document must contain at least one image without alt text | Precondition |
| AC-16 | POST-1 | After approval, querying the image record returns the alt text | Persistence |
| AC-17 | POST-2 | After approval, the image's status is "described" | Persistence |
| AC-18 | FPOST-2 | If the user cancels, no alt text is attached | Persistence |
| AC-19 | QR-1 | The generated alt text does not invent elements not visible in the image | Quality |
| AC-20 | QR-2 | The generated alt text follows WCAG guidelines (concise, no "image of" prefix, ≤ 125 chars) | Quality |
| AC-21 | QR-3 | Alt text generation completes within 10 seconds | Performance |
| AC-22 | A5 | Purpose note influences the generated alt text contextually | Functional |
| AC-23 | A6 | Multiple images can be processed sequentially | Functional |
| AC-24 | A8 | Edited alt text (not the original AI output) is what gets persisted | Persistence |

---

## C) Acceptance Oracles

### UI Oracles

| Oracle ID | What to Observe | Pass Condition |
|---|---|---|
| UI-O1 | Image selector / gallery | User can see and click on images without alt text |
| UI-O2 | Purpose note input | Free-text input field is visible and optional |
| UI-O3 | Generate button | Button is enabled when an image is selected |
| UI-O4 | Alt text preview area | Generated alt text is displayed in a review/edit textarea |
| UI-O5 | Approve button | Clicking Approve clears the review area and shows success |
| UI-O6 | Edit capability | The alt text textarea is editable before approval |
| UI-O7 | Regenerate button | Clicking Regenerate replaces the alt text with a new generation |
| UI-O8 | "Too complex" warning | A warning banner appears for complex images with a manual input option |
| UI-O9 | "No image selected" prompt | Prompt is shown when no image is selected |
| UI-O10 | Error state | Error banner with retry button on AI service failure |
| UI-O11 | Described badge | After approval, the image shows a ✅ "described" indicator |

### Database / Persistence Oracles

| Oracle ID | What to Query | Pass Condition |
|---|---|---|
| DB-O1 | `images` table — `alt_text` column | After approval, `alt_text` is populated with the approved text |
| DB-O2 | `images` table — `alt_text_status` column | After approval, status is `described` |
| DB-O3 | `images` table — before approval | `alt_text` is NULL and status is `missing` or `pending` |
| DB-O4 | `images` table — after cancel | `alt_text` remains NULL, status unchanged |
| DB-O5 | `images` table — edited alt text | The persisted text matches the user's edited version, not the AI original |

### Quality / Performance Oracles

| Oracle ID | What to Measure | Pass Condition |
|---|---|---|
| QP-O1 | Alt text content vs. image content | No invented objects, people, or text that aren't in the image |
| QP-O2 | Alt text length | ≤ 125 characters (WCAG recommended) |
| QP-O3 | Alt text prefix | Does NOT start with "image of", "picture of", "photo of" |
| QP-O4 | Generation latency | Response received within 10 seconds |
| QP-O5 | Alt text with purpose note vs. without | With note, the alt text references the stated purpose/context |

---

## D) Gherkin Feature File

```gherkin
@UC3
Feature: UC3 — GenerateImageAltText
  As a ContentDesigner
  I want to select an image, optionally add a purpose note, and have the system
  generate a WCAG-compliant alt-text description
  So that my document meets accessibility standards for non-text content.

  Background:
    Given the ContentDesigner has loaded a document containing an image without alt text

  # ── Happy-Path Scenarios ──────────────────────────────────────────────

  @UC3-S01 @happy-path
  Scenario: UC3-S01 – Generate alt text for an image without a purpose note
    When the ContentDesigner selects an image without alt text
    And the ContentDesigner clicks "Generate Alt Text"
    Then the system displays a generated alt-text description in the review area
    And the generated alt text is non-empty
    And the generated alt text does not start with "image of" or "picture of"

  @UC3-S02 @happy-path
  Scenario: UC3-S02 – Generate alt text with a purpose note
    When the ContentDesigner selects an image without alt text
    And the ContentDesigner enters the purpose note "Diagram showing the water cycle"
    And the ContentDesigner clicks "Generate Alt Text"
    Then the system displays a generated alt-text description in the review area
    And the generated alt text references the water cycle context

  @UC3-S03 @happy-path
  Scenario: UC3-S03 – Approve the generated alt text
    Given the ContentDesigner has generated alt text for an image
    When the ContentDesigner clicks "Approve"
    Then the system attaches the alt text to the image
    And the image is marked as "described"
    And a success message is displayed

  @UC3-S04 @happy-path
  Scenario: UC3-S04 – Edit alt text before approving
    Given the ContentDesigner has generated alt text for an image
    When the ContentDesigner edits the alt text to "Simplified diagram of photosynthesis"
    And the ContentDesigner clicks "Approve"
    Then the system attaches "Simplified diagram of photosynthesis" to the image
    And the image is marked as "described"

  @UC3-S05 @happy-path
  Scenario: UC3-S05 – Regenerate alt text
    Given the ContentDesigner has generated alt text for an image
    And the ContentDesigner notes the current alt text
    When the ContentDesigner clicks "Regenerate"
    Then the system displays a new alt-text description
    And the new alt text replaces the previous one in the review area

  @UC3-S06 @happy-path
  Scenario: UC3-S06 – Process multiple images sequentially
    Given the document contains two images without alt text
    When the ContentDesigner generates and approves alt text for the first image
    And the ContentDesigner generates and approves alt text for the second image
    Then both images are marked as "described"

  @UC3-S07 @happy-path
  Scenario: UC3-S07 – Image marked as described shows indicator
    Given the ContentDesigner has approved alt text for an image
    Then the image displays a "described" indicator in the UI

  # ── Negative / Precondition Scenarios ──────────────────────────────────

  @UC3-S08 @negative
  Scenario: UC3-S08 – No image selected
    When the ContentDesigner clicks "Generate Alt Text" without selecting an image
    Then the system shows a prompt: "Please select an image first"
    And no alt text is generated

  @UC3-S09 @negative
  Scenario: UC3-S09 – Image flagged as too complex
    Given the ContentDesigner selects a complex infographic image
    When the ContentDesigner clicks "Generate Alt Text"
    Then the system flags the image as too complex
    And the system asks the ContentDesigner to write the description manually
    And a manual input field is provided

  @UC3-S10 @negative
  Scenario: UC3-S10 – AI service unavailable
    Given the AI vision service is unavailable
    When the ContentDesigner selects an image and clicks "Generate Alt Text"
    Then the system displays an error message
    And a "Retry" button is available

  @UC3-S11 @negative
  Scenario: UC3-S11 – Cancel without approving
    Given the ContentDesigner has generated alt text for an image
    When the ContentDesigner clicks "Cancel"
    Then no alt text is attached to the image
    And the image remains without alt text

  @UC3-S12 @negative
  Scenario: UC3-S12 – All images already have alt text
    Given every image in the document already has alt text
    Then the system shows a message: "All images are described"
    And no "Generate Alt Text" action is needed

  @UC3-S13 @negative
  Scenario: UC3-S13 – Empty purpose note is treated as no note
    When the ContentDesigner selects an image without alt text
    And the ContentDesigner leaves the purpose note empty
    And the ContentDesigner clicks "Generate Alt Text"
    Then the system generates alt text based on the image alone
    And the generated alt text is non-empty

  @UC3-S14 @negative
  Scenario: UC3-S14 – Document contains no images
    Given the document contains no images
    Then the system shows a message: "No images found in this document"

  @UC3-S15 @negative
  Scenario: UC3-S15 – User manually writes alt text for complex image
    Given the system has flagged an image as too complex
    When the ContentDesigner types "Company revenue chart for Q3 2024" in the manual input
    And the ContentDesigner clicks "Approve"
    Then the system attaches "Company revenue chart for Q3 2024" to the image
    And the image is marked as "described"

  # ── Persistence Scenarios ──────────────────────────────────────────────

  @UC3-S16 @persistence
  Scenario: UC3-S16 – Approved alt text is persisted in the database
    Given the ContentDesigner has generated alt text for an image
    When the ContentDesigner clicks "Approve"
    Then the database record for the image contains the approved alt text
    And the database record shows the image status as "described"

  @UC3-S17 @persistence
  Scenario: UC3-S17 – Edited alt text is persisted (not the AI original)
    Given the ContentDesigner has generated alt text for an image
    When the ContentDesigner edits the alt text to "Custom user description"
    And the ContentDesigner clicks "Approve"
    Then the database record contains "Custom user description"
    And the database does NOT contain the original AI-generated text

  @UC3-S18 @persistence
  Scenario: UC3-S18 – Cancelled generation does not modify the database
    Given the database record for the image has no alt text
    And the ContentDesigner has generated alt text for the image
    When the ContentDesigner clicks "Cancel"
    Then the database record for the image still has no alt text
    And the image status remains unchanged

  @UC3-S19 @persistence
  Scenario: UC3-S19 – Manual alt text for complex image is persisted
    Given the system has flagged an image as too complex
    When the ContentDesigner writes manual alt text and approves
    Then the database record contains the manually written alt text
    And the image status is "described"

  # ── Quality / NFR Scenarios ────────────────────────────────────────────

  @UC3-S20 @quality
  Scenario: UC3-S20 – Alt text is WCAG-compliant in length
    When the ContentDesigner generates alt text for an image
    Then the generated alt text is at most 125 characters long

  @UC3-S21 @quality
  Scenario: UC3-S21 – Alt text does not use forbidden prefixes
    When the ContentDesigner generates alt text for an image
    Then the generated alt text does not start with "image of"
    And the generated alt text does not start with "picture of"
    And the generated alt text does not start with "photo of"

  @UC3-S22 @quality
  Scenario: UC3-S22 – Alt text does not hallucinate content
    Given the image contains only a single red apple on a white table
    When the ContentDesigner generates alt text for the image
    Then the alt text mentions an apple
    And the alt text does not mention objects not in the image

  @UC3-S23 @quality @performance
  Scenario: UC3-S23 – Alt text generation completes within 10 seconds
    When the ContentDesigner selects an image and clicks "Generate Alt Text"
    Then the generated alt text appears within 10 seconds

  @UC3-S24 @quality
  Scenario: UC3-S24 – Purpose note improves contextual relevance
    Given the image is a bar chart
    When the ContentDesigner enters purpose note "Sales data for 2024 by quarter"
    And the ContentDesigner clicks "Generate Alt Text"
    Then the generated alt text references sales or quarterly data

  @UC3-S25 @quality
  Scenario: UC3-S25 – Regeneration produces a different description
    Given the ContentDesigner has generated alt text for an image
    And the ContentDesigner notes the current alt text
    When the ContentDesigner clicks "Regenerate"
    Then the new alt text is different from the previously noted text
```
