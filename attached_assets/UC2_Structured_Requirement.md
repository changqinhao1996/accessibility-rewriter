# UC2 — Structured Requirement Specification: MeasureReadingLevel

## Overview

| Field | Detail |
|---|---|
| **Use case name** | MeasureReadingLevel |
| **ID** | UC2 |
| **Participating actors** | ContentDesigner (primary, initiator) · StyleRewriter (system / readability analysis engine) |
| **Goal** | Allow a ContentDesigner to highlight a passage of text, have the system calculate its Flesch–Kincaid readability score, map it to a named reading level, and optionally view a detailed breakdown that highlights the specific words and sentences that raise the score. |

---

## Preconditions

| ID | Precondition |
|---|---|
| PRE-1 | Text is present in the editor. |

---

## Main Success Flow

| Step | Actor | Action |
|---|---|---|
| 1 | ContentDesigner | Highlights a passage of text. |
| 2 | System | Calculates the readability score (e.g., Flesch–Kincaid grade) and maps it to a reading-level name (e.g., "Standard," Grades 9–12). |
| 3 | ContentDesigner | Opens the detailed breakdown. |
| 4 | System | Displays the reading-level name and grade and highlights the words and sentences that raise the score. |

---

## Success Postconditions

| ID | Postcondition |
|---|---|
| POST-1 | The ContentDesigner sees the reading-level name and grade for the selected text. |
| POST-2 | (On detailed breakdown) The ContentDesigner sees highlighted words and sentences that elevate the score. |

---

## Failure Postconditions

| ID | Postcondition |
|---|---|
| FPOST-1 | If no text is selected, no score is shown (or a prompt to select text is displayed). |
| FPOST-2 | If the selected text is too short to produce a meaningful score, the system shows a warning. |

---

## Quality Requirements

| ID | Requirement |
|---|---|
| QR-1 | The system returns the result within 200 ms so the ContentDesigner can check the reading level in real time. |

---

## Assumptions

| ID | Assumption |
|---|---|
| A1 | The readability algorithm used is Flesch–Kincaid Grade Level (the use case mentions it explicitly as an example). |
| A2 | Reading-level names follow the same five-tier taxonomy defined in UC1: Very Simple (1–3), Simple (4–5), Plain (6–8), Standard (9–12), Technical (13+). |
| A3 | The "detailed breakdown" is a secondary view triggered by user action (Step 3), not shown automatically. |
| A4 | "Words and sentences that raise the score" means items with above-average syllable count or sentence length relative to the passage. |
| A5 | The analysis is performed entirely on the client/server without calling an external AI — it is algorithmic (Flesch–Kincaid formula). |
| A6 | The system does not persist readability analysis results to the database — it is a transient, real-time measurement. |
| A7 | The score is recalculated whenever the selection changes. |
