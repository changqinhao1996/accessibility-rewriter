# D) Gherkin Feature File

```gherkin
Feature: UC1 — RewriteTextToReadingLevel
  As a ContentDesigner
  I want to rewrite document text to a chosen reading level
  So that the content is accessible to the intended audience while preserving its original meaning

  Background:
    Given the ContentDesigner is authenticated
    And a document with the following text is loaded:
      """
      Photosynthesis is the biochemical process by which chloroplasts in plant cells
      convert light energy into adenosine triphosphate, facilitating the synthesis of
      glucose from carbon dioxide and water.
      """

  # ──────────────────────────────────────────────
  # Happy-Path Scenarios
  # ──────────────────────────────────────────────

  @UC1-S01 @happy-path
  Scenario: UC1-S01 – Successful rewrite to Plain reading level
    Given the ContentDesigner selects all the source text
    And the ContentDesigner chooses reading level "Plain (Grades 6–8)"
    When the ContentDesigner submits the rewrite request
    Then the system displays the rewritten text beside the original text in a side-by-side view
    And the rewritten text preserves the original intent of the source text
    And the reading level of the rewritten text is within ±1 grade of grade 7

  @UC1-S02 @happy-path
  Scenario: UC1-S02 – ContentDesigner saves the rewritten draft
    Given the ContentDesigner selects all the source text
    And the ContentDesigner chooses reading level "Plain (Grades 6–8)"
    And the ContentDesigner submits the rewrite request
    And the system displays the rewritten draft beside the original text
    When the ContentDesigner saves the draft
    Then the system stores the rewritten draft as a new version of the document
    And a success confirmation is displayed

  @UC1-S03 @happy-path
  Scenario: UC1-S03 – Rewrite with a different reading level (e.g., Simple, Grades 3–5)
    Given the ContentDesigner selects all the source text
    And the ContentDesigner chooses reading level "Simple (Grades 3–5)"
    When the ContentDesigner submits the rewrite request
    Then the system displays the rewritten text beside the original text in a side-by-side view
    And the reading level of the rewritten text is within ±1 grade of grade 4

  @UC1-S04 @happy-path
  Scenario: UC1-S04 – Rewrite a partial text selection
    Given the ContentDesigner selects only the first sentence of the source text
    And the ContentDesigner chooses reading level "Plain (Grades 6–8)"
    When the ContentDesigner submits the rewrite request
    Then the system displays the rewritten text beside the selected original text in a side-by-side view
    And only the selected portion is rewritten

  # ──────────────────────────────────────────────
  # Negative / Precondition Scenarios
  # ──────────────────────────────────────────────

  @UC1-S05 @negative @precondition
  Scenario: UC1-S05 – Rewrite controls disabled when no document is loaded
    Given no document is loaded
    Then the rewrite controls are disabled
    And the ContentDesigner cannot submit a rewrite request

  @UC1-S06 @negative @validation
  Scenario: UC1-S06 – Validation error when source text is empty
    Given the document is loaded but contains no text
    And the ContentDesigner chooses reading level "Plain (Grades 6–8)"
    When the ContentDesigner attempts to submit the rewrite request
    Then the system displays a validation error indicating the source text is empty
    And no rewrite is performed

  @UC1-S07 @negative @validation
  Scenario: UC1-S07 – Validation error when source text is whitespace-only
    Given the document is loaded but contains only whitespace
    And the ContentDesigner chooses reading level "Plain (Grades 6–8)"
    When the ContentDesigner attempts to submit the rewrite request
    Then the system displays a validation error indicating the source text is empty
    And no rewrite is performed

  @UC1-S08 @negative @validation
  Scenario: UC1-S08 – Validation error when no reading level is selected
    Given the ContentDesigner selects all the source text
    And no reading level is chosen
    When the ContentDesigner attempts to submit the rewrite request
    Then the system displays a validation error prompting the user to select a reading level
    And no rewrite is performed

  @UC1-S09 @negative @error
  Scenario: UC1-S09 – Error when text is too unclear to rewrite safely
    Given the ContentDesigner selects source text that is ambiguous and unclear
    And the ContentDesigner chooses reading level "Plain (Grades 6–8)"
    When the ContentDesigner submits the rewrite request
    Then the system displays an error explaining that the text was too unclear to rewrite safely
    And no rewritten draft is presented
    And no new document version is created

  @UC1-S10 @negative @error
  Scenario: UC1-S10 – Error when StyleRewriter service is unavailable
    Given the ContentDesigner selects all the source text
    And the ContentDesigner chooses reading level "Plain (Grades 6–8)"
    And the StyleRewriter service is unavailable
    When the ContentDesigner submits the rewrite request
    Then the system displays a service-unavailable error message
    And the ContentDesigner is offered the option to retry

  @UC1-S11 @negative @discard
  Scenario: UC1-S11 – ContentDesigner discards the rewritten draft
    Given the ContentDesigner selects all the source text
    And the ContentDesigner chooses reading level "Plain (Grades 6–8)"
    And the ContentDesigner submits the rewrite request
    And the system displays the rewritten draft beside the original text
    When the ContentDesigner discards the draft
    Then the draft is removed from the side-by-side view
    And no new document version is created

  # ──────────────────────────────────────────────
  # Persistence Scenarios
  # ──────────────────────────────────────────────

  @UC1-S12 @persistence
  Scenario: UC1-S12 – New version is persisted after saving the draft
    Given the ContentDesigner selects all the source text
    And the ContentDesigner chooses reading level "Plain (Grades 6–8)"
    And the ContentDesigner submits the rewrite request
    And the system displays the rewritten draft
    When the ContentDesigner saves the draft
    Then a new version record exists in the database linked to the original document
    And the new version contains the rewritten text
    And the new version metadata includes the target reading level "Plain (Grades 6–8)"
    And the new version metadata includes a timestamp and the author reference

  @UC1-S13 @persistence
  Scenario: UC1-S13 – Previous versions are not modified after saving a new draft
    Given the document already has 2 existing versions
    And the ContentDesigner selects all the source text
    And the ContentDesigner chooses reading level "Plain (Grades 6–8)"
    And the ContentDesigner submits the rewrite request
    And the system displays the rewritten draft
    When the ContentDesigner saves the draft
    Then the document now has 3 versions
    And the content and metadata of the 2 previous versions remain unchanged

  @UC1-S14 @persistence
  Scenario: UC1-S14 – No version is created after discarding the draft
    Given the document has 1 existing version
    And the ContentDesigner selects all the source text
    And the ContentDesigner chooses reading level "Plain (Grades 6–8)"
    And the ContentDesigner submits the rewrite request
    And the system displays the rewritten draft
    When the ContentDesigner discards the draft
    Then the document still has exactly 1 version

  @UC1-S15 @persistence
  Scenario: UC1-S15 – No version is created on rewrite failure
    Given the document has 1 existing version
    And the ContentDesigner selects source text that is ambiguous and unclear
    And the ContentDesigner chooses reading level "Plain (Grades 6–8)"
    When the ContentDesigner submits the rewrite request
    And the system returns an error that the text was too unclear
    Then the document still has exactly 1 version

  # ──────────────────────────────────────────────
  # Quality / NFR Scenarios
  # ──────────────────────────────────────────────

  @UC1-S16 @nfr @performance
  Scenario: UC1-S16 – Rewrite completes within 700 ms at P90
    Given the ContentDesigner selects all the source text
    And the ContentDesigner chooses reading level "Plain (Grades 6–8)"
    When the ContentDesigner submits the rewrite request 100 times with representative text samples
    Then at least 90 of the 100 requests complete within 700 milliseconds
    # "Complete" = time from submit action to draft displayed in the UI

  @UC1-S17 @nfr @quality
  Scenario: UC1-S17 – Rewritten text reading level is within ±1 grade of target
    Given the ContentDesigner selects all the source text
    And the ContentDesigner chooses reading level "Plain (Grades 6–8)"
    When the ContentDesigner submits the rewrite request
    Then the readability score of the rewritten text corresponds to a grade level between 5 and 9
    # Target midpoint is grade 7; ±1 allows grades 6–8; per QR-2, ±1 of chosen target
```
