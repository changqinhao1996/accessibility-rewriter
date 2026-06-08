# UC4 — CheckDocumentAccessibility: Gherkin Feature File

```gherkin
@UC4
Feature: UC4 — CheckDocumentAccessibility
  As an AccessibilityLead
  I want to run an accessibility check on the current document
  So that I can see all WCAG 2.2 AA violations grouped by severity
  and understand which exact rule each problem breaks.

  Background:
    Given the AccessibilityLead has loaded a valid document

  # ── Happy-Path Scenarios ──────────────────────────────────────────────

  @UC4-S01 @happy-path
  Scenario: UC4-S01 – Run accessibility check on a document with issues
    Given the document contains accessibility problems
    When the AccessibilityLead clicks "Check Accessibility"
    Then the system displays a list of accessibility problems
    And the problems are grouped by severity: Critical, Serious, Minor

  @UC4-S02 @happy-path
  Scenario: UC4-S02 – Each problem shows the violated WCAG rule
    Given the document contains accessibility problems
    When the AccessibilityLead clicks "Check Accessibility"
    Then each problem displays the WCAG rule ID and name it violates
    And each problem includes a description of the issue

  @UC4-S03 @happy-path
  Scenario: UC4-S03 – Summary shows severity counts
    Given the document contains accessibility problems
    When the AccessibilityLead clicks "Check Accessibility"
    Then a summary bar shows the total number of problems
    And the summary shows the count for each severity level

  @UC4-S04 @happy-path
  Scenario: UC4-S04 – Detect missing alt text on images
    Given the document contains an image without alt text
    When the AccessibilityLead clicks "Check Accessibility"
    Then a problem is reported for WCAG rule "1.1.1 Non-text Content"
    And the problem severity is "Critical"

  @UC4-S05 @happy-path
  Scenario: UC4-S05 – Detect insufficient color contrast
    Given the document contains text with insufficient color contrast
    When the AccessibilityLead clicks "Check Accessibility"
    Then a problem is reported for WCAG rule "1.4.3 Contrast (Minimum)"
    And the problem includes the actual contrast ratio

  @UC4-S06 @happy-path
  Scenario: UC4-S06 – Detect heading hierarchy violations
    Given the document has headings that skip levels
    When the AccessibilityLead clicks "Check Accessibility"
    Then a problem is reported for heading hierarchy violation
    And the problem severity is "Serious" or "Minor"

  @UC4-S07 @happy-path
  Scenario: UC4-S07 – Detect missing form labels
    Given the document contains a form input without a label
    When the AccessibilityLead clicks "Check Accessibility"
    Then a problem is reported for WCAG rule "1.3.1 Info and Relationships"
    And the affected element is identified

  @UC4-S08 @happy-path
  Scenario: UC4-S08 – Re-check after fixing an issue shows updated results
    Given the AccessibilityLead has run a check and found problems
    When the AccessibilityLead fixes a problem in the document
    And the AccessibilityLead clicks "Check Accessibility" again
    Then the fixed problem is no longer in the results
    And the total problem count has decreased

  # ── Negative / Precondition Scenarios ──────────────────────────────────

  @UC4-S09 @negative
  Scenario: UC4-S09 – Document passes all checks
    Given the document has no accessibility problems
    When the AccessibilityLead clicks "Check Accessibility"
    Then the system displays a success message: "No accessibility issues found"
    And no problem list is shown

  @UC4-S10 @negative
  Scenario: UC4-S10 – Empty document
    Given the document has no scannable content
    When the AccessibilityLead clicks "Check Accessibility"
    Then the system displays a message indicating no content to check

  @UC4-S11 @negative
  Scenario: UC4-S11 – Scan failure with retry
    Given the accessibility scan service encounters an error
    When the AccessibilityLead clicks "Check Accessibility"
    Then the system displays an error message
    And a "Retry" button is available

  @UC4-S12 @negative
  Scenario: UC4-S12 – Loading indicator during scan
    When the AccessibilityLead clicks "Check Accessibility"
    Then a scanning indicator is shown while the check is in progress
    And the indicator disappears when results are ready

  @UC4-S13 @negative
  Scenario: UC4-S13 – No document loaded
    Given no document is loaded in the session
    When the AccessibilityLead tries to run a check
    Then the system prompts the user to load a document first

  # ── Persistence Scenarios ──────────────────────────────────────────────

  @UC4-S14 @persistence
  Scenario: UC4-S14 – Check does not write to the database
    Given the AccessibilityLead has loaded a document
    And the database has a known row count
    When the AccessibilityLead runs an accessibility check
    Then the database row count remains unchanged
    And no new records are created

  @UC4-S15 @persistence
  Scenario: UC4-S15 – Multiple checks do not create duplicate records
    Given the AccessibilityLead has loaded a document
    When the AccessibilityLead runs an accessibility check three times
    Then the database remains unchanged after all three checks

  # ── Quality / NFR Scenarios ────────────────────────────────────────────

  @UC4-S16 @quality
  Scenario: UC4-S16 – Scan covers machine-detectable WCAG 2.2 AA rules
    Given the document contains known violations across multiple WCAG criteria
    When the AccessibilityLead clicks "Check Accessibility"
    Then the results include violations from at least 3 different WCAG criteria

  @UC4-S17 @quality
  Scenario: UC4-S17 – Severity classification is accurate
    Given the document contains a missing alt text (Critical) and a skipped heading (Minor)
    When the AccessibilityLead clicks "Check Accessibility"
    Then the missing alt text is classified as "Critical"
    And the skipped heading is classified as "Minor" or "Serious"

  @UC4-S18 @quality
  Scenario: UC4-S18 – WCAG rule citations are correct
    Given the document contains text with insufficient contrast
    When the AccessibilityLead clicks "Check Accessibility"
    Then the contrast problem cites WCAG rule "1.4.3"
    And the rule name includes "Contrast"

  @UC4-S19 @quality @performance
  Scenario: UC4-S19 – Scan completes within 15 seconds
    Given the document contains content to scan
    When the AccessibilityLead clicks "Check Accessibility"
    Then the results appear within 15 seconds

  @UC4-S20 @quality
  Scenario: UC4-S20 – Each problem identifies the affected element
    Given the document contains accessibility problems
    When the AccessibilityLead clicks "Check Accessibility"
    Then each problem in the results identifies the affected element or text
```
