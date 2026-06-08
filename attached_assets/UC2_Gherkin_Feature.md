# UC2 — Gherkin Feature File: MeasureReadingLevel

```gherkin
@UC2
Feature: UC2 — MeasureReadingLevel
  As a ContentDesigner
  I want to highlight a passage of text and see its Flesch–Kincaid readability score and reading-level name
  So that I can understand the complexity of my content before rewriting it.

  Background:
    Given the ContentDesigner has loaded a document with the following text:
      """
      Photosynthesis is the biochemical process by which chloroplasts in plant cells
      convert light energy into adenosine triphosphate, facilitating the synthesis of
      glucose from carbon dioxide and water. The chlorophyll pigments within the
      thylakoid membranes absorb photon energy, initiating a cascade of electron
      transfer reactions that ultimately reduce NADP+ to NADPH.
      """

  # ── Happy-Path Scenarios ──────────────────────────────────────────────

  @UC2-S01 @happy-path
  Scenario: UC2-S01 – Highlight text and see reading-level summary
    When the ContentDesigner highlights all the text in the editor
    Then the system displays a readability badge
    And the badge shows a numeric Flesch–Kincaid grade
    And the badge shows a reading-level name from the standard taxonomy

  @UC2-S02 @happy-path
  Scenario: UC2-S02 – Grade maps to correct reading-level name
    When the ContentDesigner highlights all the text in the editor
    Then the displayed reading-level name matches the computed grade:
      | Grade Range | Expected Level Name     |
      | 1–3         | Very Simple (Grades 1–3)|
      | 4–5         | Simple (Grades 4–5)     |
      | 6–8         | Plain (Grades 6–8)      |
      | 9–12        | Standard (Grades 9–12)  |
      | 13+         | Technical (Grade 13+)   |

  @UC2-S03 @happy-path
  Scenario: UC2-S03 – Open detailed breakdown
    Given the ContentDesigner highlights all the text in the editor
    And the readability badge is visible
    When the ContentDesigner clicks "Show Details"
    Then a detailed breakdown panel opens
    And the panel displays the reading-level name
    And the panel displays the numeric grade

  @UC2-S04 @happy-path
  Scenario: UC2-S04 – Breakdown highlights complex words
    Given the ContentDesigner highlights all the text in the editor
    And the ContentDesigner opens the detailed breakdown
    Then at least one word with 3 or more syllables is visually highlighted
    And "photosynthesis" is among the highlighted words

  @UC2-S05 @happy-path
  Scenario: UC2-S05 – Breakdown highlights long sentences
    Given the ContentDesigner highlights all the text in the editor
    And the ContentDesigner opens the detailed breakdown
    Then at least one sentence longer than the passage average is visually highlighted

  @UC2-S06 @happy-path
  Scenario: UC2-S06 – Score updates when selection changes
    Given the ContentDesigner highlights all the text in the editor
    And the readability badge shows a grade
    When the ContentDesigner changes the selection to only the first sentence
    Then the readability badge updates to show a different grade
    And the update happens without a page reload

  @UC2-S07 @happy-path
  Scenario: UC2-S07 – Breakdown panel closes when toggled
    Given the ContentDesigner highlights all the text in the editor
    And the ContentDesigner opens the detailed breakdown
    When the ContentDesigner clicks "Hide Details"
    Then the detailed breakdown panel closes
    And only the readability badge remains visible

  # ── Negative / Precondition Scenarios ──────────────────────────────────

  @UC2-S08 @negative
  Scenario: UC2-S08 – No text selected shows empty state
    Given the ContentDesigner has not selected any text
    Then no readability badge is displayed
    And the system shows a prompt: "Select text to measure reading level"

  @UC2-S09 @negative
  Scenario: UC2-S09 – Single word selected shows warning
    When the ContentDesigner highlights only the word "Photosynthesis"
    Then the system shows a warning: "Selection too short for meaningful analysis"
    And no numeric grade is displayed

  @UC2-S10 @negative
  Scenario: UC2-S10 – Whitespace-only selection shows empty state
    When the ContentDesigner highlights only whitespace characters
    Then no readability badge is displayed
    And the system shows a prompt: "Select text to measure reading level"

  @UC2-S11 @negative
  Scenario: UC2-S11 – Empty editor shows no analysis
    Given the editor contains no text
    Then the readability measurement controls are disabled or hidden

  # ── Persistence Scenarios ──────────────────────────────────────────────

  @UC2-S12 @persistence
  Scenario: UC2-S12 – Analysis does not persist to database
    Given the ContentDesigner highlights all the text in the editor
    And the system displays a readability badge
    Then no new rows are created in the documents table
    And no new rows are created in the document_versions table

  @UC2-S13 @persistence
  Scenario: UC2-S13 – Same text produces identical score on re-selection
    Given the ContentDesigner highlights all the text in the editor
    And notes the displayed grade as "first_grade"
    When the ContentDesigner clears the selection
    And the ContentDesigner highlights all the text again
    Then the displayed grade equals "first_grade"

  # ── Quality / NFR Scenarios ────────────────────────────────────────────

  @UC2-S14 @quality @performance
  Scenario: UC2-S14 – Score appears within 200ms for short text
    When the ContentDesigner highlights all the text in the editor
    Then the readability badge appears within 200 milliseconds

  @UC2-S15 @quality @performance
  Scenario: UC2-S15 – Score appears within 200ms for long text (2000 words)
    Given the editor contains a 2000-word passage
    When the ContentDesigner highlights all the text
    Then the readability badge appears within 200 milliseconds

  @UC2-S16 @quality
  Scenario: UC2-S16 – Rapid selection changes do not freeze UI
    When the ContentDesigner rapidly changes the selection 10 times in 2 seconds
    Then the UI remains responsive throughout
    And the final readability badge matches the final selection

  @UC2-S17 @quality
  Scenario: UC2-S17 – Known text produces expected grade (accuracy)
    Given the editor contains exactly:
      """
      The cat sat on the mat. The dog ran fast.
      """
    When the ContentDesigner highlights all the text
    Then the displayed Flesch–Kincaid grade is within ±0.5 of the expected grade for that text

  @UC2-S18 @quality
  Scenario: UC2-S18 – Highlighted complex words match syllable criterion
    Given the ContentDesigner highlights all the text in the editor
    And the ContentDesigner opens the detailed breakdown
    Then every highlighted word has 3 or more syllables
    And no word with fewer than 3 syllables is highlighted as complex

  @UC2-S19 @quality
  Scenario: UC2-S19 – Highlighted long sentences match length criterion
    Given the ContentDesigner highlights all the text in the editor
    And the ContentDesigner opens the detailed breakdown
    Then every highlighted sentence has a word count above the passage average
    And no sentence at or below the average word count is highlighted as long
```
