# UC3 — Structured Requirement Specification: GenerateImageAltText

---

## Use Case Name
**GenerateImageAltText**

## Participating Actors
| Actor | Role |
|---|---|
| **ContentDesigner** | Initiator — selects an image, optionally adds a purpose note, reviews and approves the generated alt text |
| **AccessibilityChecker** | System service — analyzes the image (and optional note), generates a WCAG-compliant alt-text description |

## Goal
Enable the ContentDesigner to generate, review, and attach WCAG-compliant alt-text descriptions to images in a document, so that the document meets accessibility standards.

## Preconditions
| ID | Precondition |
|---|---|
| PRE-1 | The document contains at least one image without alt text |

## Main Success Flow
| Step | Actor | Action |
|---|---|---|
| 1 | ContentDesigner | Selects an image in the document and, optionally, adds a note describing the image's purpose |
| 2 | System (AccessibilityChecker) | Analyzes the image and the note, generates a WCAG-compliant alt-text description, and displays it for review |
| 3 | ContentDesigner | Approves the alt text |
| 4 | System | Attaches the approved alt text to the image and marks the image as described |

## Alternative / Failure Flows
| ID | Condition | Action |
|---|---|---|
| ALT-1 | Image is too complex for AI to describe accurately | System flags the image as too complex and asks the ContentDesigner to write the description manually |
| ALT-2 | ContentDesigner rejects the generated alt text | ContentDesigner can edit the alt text before approving, or regenerate |
| ALT-3 | No image selected | System shows a prompt to select an image |
| ALT-4 | AI service is unavailable | System shows an error message and allows retry |

## Success Postconditions
| ID | Postcondition |
|---|---|
| POST-1 | The image has an approved alt-text description attached |
| POST-2 | The image is marked as "described" (has alt text) |

## Failure Postconditions
| ID | Postcondition |
|---|---|
| FPOST-1 | The system flags the image as too complex and asks the ContentDesigner to write the description manually |
| FPOST-2 | No alt text is attached; the image remains in its original state |

## Quality Requirements
| ID | Requirement |
|---|---|
| QR-1 | The generated alt text describes **only** what appears in the image and never invents elements that are not present (faithfulness / no hallucination) |
| QR-2 | The generated alt text is WCAG-compliant (concise, descriptive, ≤ 125 characters recommended, avoids "image of" / "picture of" prefixes) |
| QR-3 | The alt text generation completes within a reasonable time (≤ 10 seconds) |

## Assumptions
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
