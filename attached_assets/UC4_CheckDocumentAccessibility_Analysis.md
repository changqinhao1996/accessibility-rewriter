# UC4 — CheckDocumentAccessibility: Analysis & Acceptance Tests

---

## A) Structured Requirement Specification

### Use Case Name
**CheckDocumentAccessibility**

### Participating Actors
| Actor | Role |
|---|---|
| **AccessibilityLead** | Initiator — requests an accessibility check of the current document, reviews the results |
| **AccessibilityChecker** | System service — loads active WCAG 2.2 AA rules, scans the document's structure, contrast, and text, groups problems by severity, and displays the results |

### Goal
Enable the AccessibilityLead to run a comprehensive WCAG 2.2 AA compliance check on the current document, see all identified accessibility problems grouped by severity (Critical, Serious, Minor), and understand which exact rule each problem violates.

### Preconditions
| ID | Precondition |
|---|---|
| PRE-1 | A valid document is loaded in the session |

### Main Success Flow
| Step | Actor | Action |
|---|---|---|
| 1 | AccessibilityLead | Requests an accessibility check of the current document |
| 2 | System (AccessibilityChecker) | Loads the active WCAG 2.2 AA rules, scans the document's structure, contrast, and text, and groups the problems it finds by severity (Critical, Serious, Minor) |
| 3 | AccessibilityLead | Opens the results |
| 4 | System | Displays the list of problems and shows the exact rule that each problem breaks |

### Alternative / Failure Flows
| ID | Condition | Action |
|---|---|---|
| ALT-1 | Document has no accessibility problems | System displays a "no issues found" success message |
| ALT-2 | Document is empty or has no scannable content | System displays a message indicating insufficient content to check |
| ALT-3 | Scan fails or times out | System shows an error message and allows retry |

### Success Postconditions
| ID | Postcondition |
|---|---|
| POST-1 | The AccessibilityLead sees a complete list of the document's accessibility problems |
| POST-2 | Each problem is mapped to the exact WCAG 2.2 AA rule it violates |
| POST-3 | Problems are grouped by severity: Critical, Serious, Minor |

### Failure Postconditions
| ID | Postcondition |
|---|---|
| FPOST-1 | A "no issues found" message is displayed if the document passes all checks |
| FPOST-2 | An error message with retry option is shown if the scan fails |

### Quality Requirements
| ID | Requirement |
|---|---|
| QR-1 | The check covers 100% of the machine-detectable WCAG 2.2 AA rules |
| QR-2 | Results are grouped by severity (Critical, Serious, Minor) with accurate severity classification |
| QR-3 | Each problem cites the specific WCAG 2.2 criterion it violates (e.g., "1.4.3 Contrast (Minimum)") |
| QR-4 | The scan completes within a reasonable time (≤ 15 seconds for typical documents) |

### Assumptions
| ID | Assumption |
|---|---|
| A1 | "WCAG 2.2 AA rules" refers to the Level A and Level AA success criteria from the Web Content Accessibility Guidelines 2.2 |
| A2 | "Machine-detectable" means rules that can be verified programmatically — some WCAG criteria require human judgment and are excluded |
| A3 | The system scans structure (heading hierarchy, landmarks, ARIA), contrast (color contrast ratios), and text (language, link text, form labels) |
| A4 | Severity classification follows a standard mapping: Critical = perceivability/operability barriers; Serious = significant usability issues; Minor = best-practice deviations |
| A5 | The document is in HTML format and is scanned client-side or via a backend accessibility engine |
| A6 | The scan operates on the current state of the document (including any edits from UC1/UC2/UC3) |
| A7 | Scan results are transient — they are computed on demand and are NOT persisted in the database |
| A8 | The AccessibilityLead can re-run the check at any time to see updated results |

---

## B) Acceptance Checks Table

| Check ID | Source | Acceptance Check | Type |
|---|---|---|---|
| AC-01 | Flow Step 1 | AccessibilityLead can initiate an accessibility check via a "Check Accessibility" button | UI |
| AC-02 | Flow Step 2 | System scans the document's structure for heading hierarchy violations | Functional |
| AC-03 | Flow Step 2 | System scans for color contrast issues | Functional |
| AC-04 | Flow Step 2 | System scans text-level issues (missing lang, vague link text, missing form labels) | Functional |
| AC-05 | Flow Step 2 | Problems are grouped by severity: Critical, Serious, Minor | UI / Functional |
| AC-06 | Flow Step 2 | A loading/scanning indicator is shown while the check is in progress | UI |
| AC-07 | Flow Step 3 | AccessibilityLead can view the results in an organized panel | UI |
| AC-08 | Flow Step 4 | Each problem shows the exact WCAG rule it violates (e.g., "1.4.3 Contrast (Minimum)") | UI |
| AC-09 | Flow Step 4 | Each problem shows a description of what is wrong | UI |
| AC-10 | Flow Step 4 | Each problem shows the affected element or text excerpt | UI |
| AC-11 | ALT-1 | If no problems found, a success message is displayed | UI |
| AC-12 | ALT-2 | If document is empty, a message indicates insufficient content | UI / Validation |
| AC-13 | ALT-3 | If scan fails, an error message with retry button is shown | Error handling |
| AC-14 | PRE-1 | A document must be loaded before the check can run | Precondition |
| AC-15 | POST-1 | The results list contains all detected problems | Functional |
| AC-16 | POST-2 | Each result item references a specific WCAG criterion | Functional |
| AC-17 | POST-3 | Results are organized into severity groups with correct counts | UI |
| AC-18 | QR-1 | The scanner covers all machine-detectable WCAG 2.2 AA criteria | Quality |
| AC-19 | QR-2 | Severity classification is accurate (Critical ≠ Minor) | Quality |
| AC-20 | QR-3 | Each problem cites the correct WCAG criterion number and name | Quality |
| AC-21 | QR-4 | Scan completes within 15 seconds for typical documents | Performance |
| AC-22 | A7 | Scan results are transient and not persisted in the database | Persistence (negative) |
| AC-23 | A8 | Re-running the check reflects any changes made since the last scan | Functional |
| AC-24 | A4 | Severity counts (Critical, Serious, Minor) are displayed in a summary | UI |

---

## C) Acceptance Oracles

### UI Oracles

| Oracle ID | What to Observe | Pass Condition |
|---|---|---|
| UI-O1 | Check Accessibility button | Button is visible and clickable when a document is loaded |
| UI-O2 | Loading/scanning state | A spinner or progress indicator appears during the scan |
| UI-O3 | Results panel | After scan, a results panel displays with organized problem list |
| UI-O4 | Severity grouping | Problems are grouped under Critical, Serious, and Minor sections |
| UI-O5 | Severity counts | Each group header shows the count of problems in that severity |
| UI-O6 | Problem detail | Each problem shows: description, affected element, WCAG rule ID and name |
| UI-O7 | No-issues state | If no problems found, a success banner says "No accessibility issues found" |
| UI-O8 | Empty document state | If document is empty, a message says "No content to check" or similar |
| UI-O9 | Error state | Error banner with retry button on scan failure |
| UI-O10 | Re-check capability | Running the check again produces fresh results |
| UI-O11 | Summary bar | Total problem count and severity breakdown are shown in a summary |

### Database / Persistence Oracles

| Oracle ID | What to Query | Pass Condition |
|---|---|---|
| DB-O1 | Database tables after running check | No new rows are created — UC4 is transient |
| DB-O2 | Document/version count before and after | Counts remain unchanged — check does not modify the database |

### Quality / Performance Oracles

| Oracle ID | What to Measure | Pass Condition |
|---|---|---|
| QP-O1 | WCAG rule coverage | Scanner checks all machine-detectable WCAG 2.2 AA criteria |
| QP-O2 | Severity accuracy | Known contrast violation classified as Critical or Serious, not Minor |
| QP-O3 | Rule citation accuracy | Each problem cites the correct WCAG criterion number (e.g., "1.4.3") and name |
| QP-O4 | Scan latency | Results appear within 15 seconds for a typical document |
| QP-O5 | Re-scan freshness | After fixing an issue, re-running the check no longer reports it |

---

## D) Gherkin Feature File

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
