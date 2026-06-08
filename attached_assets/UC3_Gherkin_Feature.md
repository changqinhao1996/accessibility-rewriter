# UC3 — Gherkin Feature File: GenerateImageAltText

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
