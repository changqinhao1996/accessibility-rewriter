# UC4 — CheckDocumentAccessibility: Structured Requirement

---

## Use Case Name
**CheckDocumentAccessibility**

## Participating Actors
| Actor | Role |
|---|---|
| **AccessibilityLead** | Initiator — requests an accessibility check of the current document, reviews the results |
| **AccessibilityChecker** | System service — loads active WCAG 2.2 AA rules, scans the document's structure, contrast, and text, groups problems by severity, and displays the results |

## Goal
Enable the AccessibilityLead to run a comprehensive WCAG 2.2 AA compliance check on the current document, see all identified accessibility problems grouped by severity (Critical, Serious, Minor), and understand which exact rule each problem violates.

## Preconditions
| ID | Precondition |
|---|---|
| PRE-1 | A valid document is loaded in the session |

## Main Success Flow
| Step | Actor | Action |
|---|---|---|
| 1 | AccessibilityLead | Requests an accessibility check of the current document |
| 2 | System (AccessibilityChecker) | Loads the active WCAG 2.2 AA rules, scans the document's structure, contrast, and text, and groups the problems it finds by severity (Critical, Serious, Minor) |
| 3 | AccessibilityLead | Opens the results |
| 4 | System | Displays the list of problems and shows the exact rule that each problem breaks |

## Alternative / Failure Flows
| ID | Condition | Action |
|---|---|---|
| ALT-1 | Document has no accessibility problems | System displays a "no issues found" success message |
| ALT-2 | Document is empty or has no scannable content | System displays a message indicating insufficient content to check |
| ALT-3 | Scan fails or times out | System shows an error message and allows retry |

## Success Postconditions
| ID | Postcondition |
|---|---|
| POST-1 | The AccessibilityLead sees a complete list of the document's accessibility problems |
| POST-2 | Each problem is mapped to the exact WCAG 2.2 AA rule it violates |
| POST-3 | Problems are grouped by severity: Critical, Serious, Minor |

## Failure Postconditions
| ID | Postcondition |
|---|---|
| FPOST-1 | A "no issues found" message is displayed if the document passes all checks |
| FPOST-2 | An error message with retry option is shown if the scan fails |

## Quality Requirements
| ID | Requirement |
|---|---|
| QR-1 | The check covers 100% of the machine-detectable WCAG 2.2 AA rules |
| QR-2 | Results are grouped by severity (Critical, Serious, Minor) with accurate severity classification |
| QR-3 | Each problem cites the specific WCAG 2.2 criterion it violates (e.g., "1.4.3 Contrast (Minimum)") |
| QR-4 | The scan completes within a reasonable time (≤ 15 seconds for typical documents) |

## Assumptions
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
