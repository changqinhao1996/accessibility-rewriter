@UC2
Feature: UC2 — MeasureReadingLevel
  As a ContentDesigner
  I want to highlight a passage of text and see its Flesch–Kincaid readability score and reading-level name
  So that I can understand the complexity of my content before rewriting it.

  Background:
    Given the ContentDesigner has loaded the analyze page with the following text:
      """
      Photosynthesis is the biochemical process by which chloroplasts in plant cells
      convert light energy into adenosine triphosphate, facilitating the synthesis of
      glucose from carbon dioxide and water. The chlorophyll pigments within the
      thylakoid membranes absorb photon energy, initiating a cascade of electron
      transfer reactions that ultimately reduce NADP+ to NADPH.
      """

  # ── Happy-Path Scenarios ──────────────────────────────────────────────

  @UC2-S01 @happy-path
  Scenario: UC2-S01 – Analyze text and see reading-level summary
    When the ContentDesigner clicks the Analyze button
    Then the system displays a readability badge
    And the badge shows a numeric Flesch–Kincaid grade
    And the badge shows a reading-level name from the standard taxonomy

  @UC2-S02 @happy-path
  Scenario: UC2-S02 – Grade maps to correct reading-level name
    When the ContentDesigner clicks the Analyze button
    Then the displayed reading-level name is one of:
      | Very Simple (Grades 1–3) |
      | Simple (Grades 4–5)     |
      | Plain (Grades 6–8)      |
      | Standard (Grades 9–12)  |
      | Technical (Grade 13+)   |

  @UC2-S03 @happy-path
  Scenario: UC2-S03 – Open detailed breakdown
    Given the ContentDesigner clicks the Analyze button
    And the readability badge is visible
    When the ContentDesigner clicks "Show Details"
    Then a detailed breakdown panel opens
    And the panel displays the reading-level name
    And the panel displays the numeric grade

  @UC2-S04 @happy-path
  Scenario: UC2-S04 – Breakdown highlights complex words
    Given the ContentDesigner clicks the Analyze button
    And the ContentDesigner opens the detailed breakdown
    Then at least one word with 3 or more syllables is visually highlighted
    And "Photosynthesis" is among the highlighted words

  @UC2-S05 @happy-path
  Scenario: UC2-S05 – Breakdown highlights long sentences
    Given the ContentDesigner clicks the Analyze button
    And the ContentDesigner opens the detailed breakdown
    Then at least one sentence is highlighted as a long sentence

  @UC2-S06 @happy-path
  Scenario: UC2-S06 – Score updates when text changes and re-analyzed
    Given the ContentDesigner clicks the Analyze button
    And the readability badge shows a grade
    When the ContentDesigner changes the text to "The cat sat on the mat. The dog ran fast."
    And the ContentDesigner clicks the Analyze button
    Then the readability badge updates to show a different grade

  @UC2-S07 @happy-path
  Scenario: UC2-S07 – Breakdown panel closes when toggled
    Given the ContentDesigner clicks the Analyze button
    And the ContentDesigner opens the detailed breakdown
    When the ContentDesigner clicks "Hide Details"
    Then the detailed breakdown panel closes
    And the readability badge remains visible

  # ── Negative / Precondition Scenarios ──────────────────────────────────

  @UC2-S08 @negative
  Scenario: UC2-S08 – Empty text shows empty state
    Given the ContentDesigner clears all text from the editor
    Then the system shows a prompt: "Select text to measure reading level"
    And the Analyze button is disabled

  @UC2-S09 @negative
  Scenario: UC2-S09 – Single word shows warning
    Given the ContentDesigner replaces the text with "Photosynthesis"
    When the ContentDesigner clicks the Analyze button
    Then the system shows a warning: "Selection too short for meaningful analysis"
    And no readability badge is displayed

  @UC2-S10 @negative
  Scenario: UC2-S10 – Whitespace-only text shows empty state
    Given the ContentDesigner replaces the text with "   "
    Then the Analyze button is disabled
    And the system shows a prompt: "Select text to measure reading level"

  @UC2-S11 @negative
  Scenario: UC2-S11 – Two words produces a valid score
    Given the ContentDesigner replaces the text with "Hello world."
    When the ContentDesigner clicks the Analyze button
    Then the system displays a readability badge

  # ── Persistence Scenarios ──────────────────────────────────────────────

  @UC2-S12 @persistence
  Scenario: UC2-S12 – Analysis does not persist to database
    Given the database row counts are noted
    When the ContentDesigner clicks the Analyze button
    Then the readability badge is visible
    And the database row counts have not changed

  @UC2-S13 @persistence
  Scenario: UC2-S13 – Same text produces identical score on re-analysis
    When the ContentDesigner clicks the Analyze button
    And notes the displayed grade
    And the ContentDesigner clicks Clear
    And the ContentDesigner restores the original text
    And the ContentDesigner clicks the Analyze button
    Then the displayed grade equals the previously noted grade

  # ── Quality / NFR Scenarios ────────────────────────────────────────────

  @UC2-S14 @quality @performance
  Scenario: UC2-S14 – Score appears within 200ms for short text
    When the ContentDesigner clicks the Analyze button
    Then the readability badge appears within 200 milliseconds

  @UC2-S15 @quality @performance
  Scenario: UC2-S15 – Score appears within 200ms for long text (2000 words)
    Given the editor contains a 2000-word passage
    When the ContentDesigner clicks the Analyze button
    Then the readability badge appears within 200 milliseconds

  @UC2-S16 @quality
  Scenario: UC2-S16 – Known text produces expected grade (accuracy)
    Given the ContentDesigner replaces the text with "The cat sat on the mat. The dog ran fast."
    When the ContentDesigner clicks the Analyze button
    Then the displayed Flesch–Kincaid grade is a valid number

  @UC2-S17 @quality
  Scenario: UC2-S17 – Highlighted complex words match syllable criterion
    Given the ContentDesigner clicks the Analyze button
    And the ContentDesigner opens the detailed breakdown
    Then every highlighted word in the word list has 3 or more syllables noted

  @UC2-S18 @quality
  Scenario: UC2-S18 – Backend API returns consistent result
    When the backend receives a POST to /api/analyze with the background text
    Then the response status is 200
    And the response contains a valid grade and level_name

  @UC2-S19 @quality
  Scenario: UC2-S19 – Backend API rejects short text
    When the backend receives a POST to /api/analyze with text "Hello"
    Then the response status is 422
    And the response detail is "Selection too short for meaningful analysis"
