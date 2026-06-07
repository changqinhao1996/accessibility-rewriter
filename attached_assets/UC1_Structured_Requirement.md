# A) Structured Requirement Specification

## Use Case 1 — RewriteTextToReadingLevel

| Field | Detail |
|---|---|
| **Use case name** | RewriteTextToReadingLevel |
| **ID** | UC1 |
| **Participating actors** | **ContentDesigner** (primary, initiator) · **StyleRewriter** (system / AI engine the System communicates with) |
| **Goal** | Allow a ContentDesigner to rewrite a loaded document's text to a chosen target reading level, review the result side-by-side with the original, and persist the accepted draft as a new document version. |

## Preconditions

| ID | Precondition |
|---|---|
| PRE-1 | The ContentDesigner has loaded a document that contains text. |

## Main Success Flow

| Step | Actor | Action |
|---|---|---|
| 1 | ContentDesigner | Selects the source text and chooses a target reading level (e.g., "Plain," covering Grades 6–8). |
| 2 | System | Validates the text and loads the rules for the chosen reading level. |
| 3 | ContentDesigner | Submits the rewrite request. |
| 4 | System | Rewrites the text to the chosen reading level, preserves the original intent, and presents the rewritten draft beside the original text. |
| 5 | ContentDesigner | Reviews the draft and saves it. |
| 6 | System | Stores the rewritten draft as a new version of the document. |

## Extension / Alternative Flows

| ID | Condition | Flow |
|---|---|---|
| EXT-2a | Text is empty or whitespace-only | System displays a validation error; flow returns to Step 1. |
| EXT-2b | No reading level selected | System displays a validation error prompting the user to select a reading level; flow returns to Step 1. |
| EXT-4a | Text is too unclear to rewrite safely | System returns an error explaining that the text was too unclear to rewrite safely (per Exit Condition). |
| EXT-4b | StyleRewriter service is unavailable | System displays a service-unavailable error; ContentDesigner may retry. |
| EXT-5a | ContentDesigner discards the draft | Draft is not saved; document remains unchanged. No new version is created. |

## Success Postconditions

| ID | Postcondition |
|---|---|
| POST-S1 | The ContentDesigner has saved a rewritten draft that matches the chosen reading level. |
| POST-S2 | A new version of the document is stored in the database. |

## Failure Postconditions

| ID | Postcondition |
|---|---|
| POST-F1 | The System has returned an error explaining that the text was too unclear to rewrite safely. |
| POST-F2 | No new document version has been created. |

## Quality Requirements

| ID | Requirement |
|---|---|
| QR-1 | The System produces the rewrite within 700 ms (P90). |
| QR-2 | The reading level of the output stays within ±1 grade of the chosen target. |

## Assumptions

| ID | Assumption |
|---|---|
| A1 | A "reading level" maps to a well-defined grade range (e.g., "Plain" = Grades 6–8). |
| A2 | The StyleRewriter is an AI/NLP back-end service accessible via an internal API. |
| A3 | Document versioning is append-only; saving a draft never overwrites a prior version. |
| A4 | "Source text" may be the full document or a user-selected portion; the system treats whatever is selected as the input. |
| A5 | The side-by-side view is rendered in the same UI session; no page reload is required. |
| A6 | Reading-level measurement uses a standard readability metric (e.g., Flesch-Kincaid). |
| A7 | The 700 ms P90 latency is measured from the moment the rewrite request is submitted (Step 3) until the draft is presented (Step 4). |
| A8 | Authentication and authorization of the ContentDesigner are handled outside this use case. |
