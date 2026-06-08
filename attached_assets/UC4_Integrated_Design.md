# UC4 — CheckDocumentAccessibility: Integrated Design

---

## A) UI Design Summary

### Page / Component: AccessibilityPage

UC4 adds a new **♿ Accessibility** tab to the application. This is a dedicated page where the AccessibilityLead can run a WCAG 2.2 AA compliance check on the current document and view all identified problems grouped by severity.

### Component Hierarchy

```
AccessibilityPage (new — UC4)
├── CheckButton                  — "♿ Check Accessibility" action button
├── ScanningIndicator            — Spinner shown while scan is in progress
├── SummaryBar                   — Total problem count + severity breakdown
│   ├── TotalCount               — "12 issues found"
│   ├── CriticalCount            — "3 Critical"
│   ├── SeriousCount             — "5 Serious"
│   └── MinorCount               — "4 Minor"
├── SeverityGroup                — Collapsible section per severity level (×3)
│   ├── GroupHeader              — Severity name + count + expand/collapse toggle
│   └── ProblemCard (×N)         — Individual violation detail
│       ├── RuleId               — WCAG criterion number (e.g., "1.4.3")
│       ├── RuleName             — WCAG criterion name (e.g., "Contrast (Minimum)")
│       ├── Description          — Human-readable explanation of the violation
│       └── AffectedElement      — The element/text that caused the violation
├── NoIssuesMessage              — "No accessibility issues found" success banner
├── EmptyDocumentMessage         — "No content to check" info banner
├── NoDocumentMessage            — "Load a document first" info banner
└── ErrorBanner                  — Error message + Retry button
```

### UI Elements Inventory

| Element ID | Type | Visible When | Content / Behavior |
|---|---|---|---|
| `accessibility-page` | Container | Always | Page wrapper |
| `check-btn` | Button | Always | "♿ Check Accessibility" — initiates the scan |
| `scanning-indicator` | Spinner/animation | Scan in progress | "Scanning for accessibility issues…" |
| `summary-bar` | Container | Problems found | Shows total + per-severity counts |
| `total-count` | Span | Problems found | "N issues found" |
| `critical-count` | Badge | Problems found | Red badge with Critical count |
| `serious-count` | Badge | Problems found | Orange badge with Serious count |
| `minor-count` | Badge | Problems found | Yellow badge with Minor count |
| `critical-group` | Collapsible section | Critical issues exist | Section header + problem cards |
| `serious-group` | Collapsible section | Serious issues exist | Section header + problem cards |
| `minor-group` | Collapsible section | Minor issues exist | Section header + problem cards |
| `problem-card` | Card | Per problem | Shows rule ID, name, description, element |
| `rule-id` | Span | Per problem card | WCAG criterion number (e.g., "1.4.3") |
| `rule-name` | Span | Per problem card | WCAG criterion name (e.g., "Contrast (Minimum)") |
| `problem-description` | Text | Per problem card | Human-readable issue description |
| `affected-element` | Code/text | Per problem card | The element or text excerpt causing the violation |
| `no-issues-msg` | Success banner | No problems found | "No accessibility issues found ✅" |
| `empty-doc-msg` | Info banner | Document is empty | "No content to check" |
| `no-doc-msg` | Info banner | No document loaded | "Load a document to check accessibility" |
| `error-banner` | Error banner | Scan error | Error message text |
| `retry-btn` | Button | Scan error | "🔄 Retry" |

### State Machine

```
┌────────────┐  click Check    ┌──────────────┐    scan done     ┌──────────────────┐
│  idle      │────────────────→│ scanning     │─────────────────→│ results-shown    │
│ (button    │                 │ (spinner     │                   │ (summary +       │
│  shown)    │                 │  visible)    │                   │  severity groups)│
└────────────┘                 └──────┬───────┘                   └────────┬─────────┘
                                      │                                    │
                               error  │                          re-check  │
                                      │                                    │
                                      ↓                                    ↓
                              ┌──────────────┐                    ┌────────────┐
                              │ error        │                    │ idle       │
                              │ (banner +    │                    │ (ready for │
                              │  retry btn)  │                    │  re-check) │
                              └──────────────┘                    └────────────┘

Special states:
  no-issues   → success banner (no severity groups shown)
  empty-doc   → info banner (no check button functionality)
  no-document → info banner with load-document prompt
```

---

## B) Database Design Summary

### No New Tables Required

UC4 is **transient** — scan results are computed on demand and are NOT persisted in the database. The check reads existing document/content data but writes nothing.

### Existing Tables Referenced (Read-Only)

| Table | UC4 Usage |
|---|---|
| `documents` | Provides the document content to scan |
| `document_versions` | Latest version supplies the HTML/text content |
| `images` | Checked for missing alt text (WCAG 1.1.1) |

### Seed Data

| Seed Scenario | Content | Purpose |
|---|---|---|
| Document with violations | HTML with: missing alt text, low contrast text, skipped headings, unlabeled form inputs | S01–S08, S16–S20 (happy path + quality) |
| Clean document | Well-structured HTML with proper headings, alt text, contrast, labels | S09 (no issues) |
| Empty document | Blank or minimal content | S10 (empty doc) |
| No document | Session without loaded document | S13 (no document) |

### Reset Rules

| Reset Action | When |
|---|---|
| Reset document content | Before each scenario — set to scenario-appropriate content |
| No table inserts/deletes by UC4 | Verified in S14, S15 (persistence scenarios) |

---

## C) Service / Control Design Summary

### Key Design Decision: Server-Side WCAG Scanning

The accessibility check runs **server-side** using a rule engine that scans the document's HTML content against WCAG 2.2 AA criteria. This mirrors how production accessibility tools (axe-core, WAVE) operate.

### Service: `AccessibilityService` (Python — server-side)

```
AccessibilityService
├── check_document(document_id) → AccessibilityReport
│   ├── Load latest document content from DB
│   ├── If content is empty/blank → return empty-doc error
│   ├── Call AccessibilityCheckerPort.scan(html_content)
│   ├── Group results by severity (Critical, Serious, Minor)
│   ├── Sort within each group by rule ID
│   └── Return { problems[], summary { total, critical, serious, minor } }
```

### Port: `AccessibilityCheckerPort` (Interface)

```python
class AccessibilityCheckerPort(ABC):
    @abstractmethod
    async def scan(self, html_content: str) -> list[AccessibilityProblem]:
        """Scan HTML content for WCAG 2.2 AA violations."""
        ...
```

### Adapters

| Adapter | When Used | Behavior |
|---|---|---|
| `AxeAccessibilityChecker` | Production / Demo | Uses axe-core (via Python wrapper) to scan HTML for WCAG violations |
| `FakeAccessibilityChecker` | Tests | Returns canned problems; can simulate clean doc, error, and specific violation types |

### Types

```python
@dataclass
class AccessibilityProblem:
    rule_id: str              # WCAG criterion number (e.g., "1.4.3")
    rule_name: str            # WCAG criterion name (e.g., "Contrast (Minimum)")
    severity: str             # "critical", "serious", or "minor"
    description: str          # Human-readable explanation
    affected_element: str     # HTML snippet or text causing the violation

@dataclass
class AccessibilityReport:
    problems: list[AccessibilityProblem]
    summary: dict             # { total, critical, serious, minor }
```

### API Endpoints

| Method | Path | Purpose | Response |
|---|---|---|---|
| `POST` | `/api/accessibility/check` | Run WCAG scan on a document | 200: `{ problems: [...], summary: {...} }` |

Request body:
```json
{
  "document_id": "11111111-1111-1111-1111-111111111111"
}
```

Response (200):
```json
{
  "problems": [
    {
      "rule_id": "1.1.1",
      "rule_name": "Non-text Content",
      "severity": "critical",
      "description": "Image element is missing alt attribute",
      "affected_element": "<img src=\"photo.jpg\">"
    },
    {
      "rule_id": "1.4.3",
      "rule_name": "Contrast (Minimum)",
      "severity": "serious",
      "description": "Text has insufficient contrast ratio of 2.5:1 (minimum 4.5:1)",
      "affected_element": "<p style=\"color: #aaa\">Light text</p>"
    }
  ],
  "summary": {
    "total": 5,
    "critical": 2,
    "serious": 2,
    "minor": 1
  }
}
```

Error response (when scan fails — 503):
```json
{
  "detail": "Accessibility scan service is unavailable"
}
```

Empty document response (422):
```json
{
  "detail": "No content to check"
}
```

### External Dependencies

| Dependency | UC4 Usage |
|---|---|
| `axe-core` (via `axe-core-python` or subprocess) | Production WCAG scanning engine |
| **AccessibilityCheckerPort** | Adapter pattern (same approach as UC1's StyleRewriterPort, UC3's VisionAnalyzerPort) |

### Test Endpoint (for FakeAccessibilityChecker Mode Switching)

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/test/accessibility-mode` | Switch fake checker mode: `default`, `clean`, `error`, `empty` |

---

## D) Acceptance Harness Design

### Framework

Same as UC1/UC2/UC3: **Behave** (Python) + **Playwright** for browser automation.

### Before Each Scenario

| Action | Detail |
|---|---|
| Reset document content | Set document to scenario-appropriate HTML content via DB update |
| Configure FakeAccessibilityChecker | Set mode: default (with violations), clean, error, or specific violation types |
| Navigate to Accessibility page | Open `http://localhost:5173` → click "♿ Accessibility" tab |

### Scenario-Specific Seeding

| Scenario Tags | Seed Data | FakeChecker Mode |
|---|---|---|
| `@happy-path` (S01–S08) | Document with mixed violations (missing alt text, low contrast, skipped headings, unlabeled inputs) | `default` — returns canned problems |
| `UC4-S04` | Document with image missing alt text | `default` — includes 1.1.1 violation |
| `UC4-S05` | Document with low contrast text | `default` — includes 1.4.3 violation with ratio |
| `UC4-S06` | Document with skipped heading levels | `default` — includes heading violation |
| `UC4-S07` | Document with unlabeled form input | `default` — includes 1.3.1 violation |
| `UC4-S08` | Same as S01, then update document, re-check | `default` then `fewer` mode |
| `UC4-S09` | Well-formed accessible document | `clean` — returns empty problem list |
| `UC4-S10` | Empty document | `empty` — returns empty-doc error |
| `UC4-S11` | Any document | `error` — raises ServiceUnavailableError |
| `UC4-S13` | No document loaded | N/A — test without navigating to doc |
| `UC4-S14`, `UC4-S15` | Any document | `default` — verify DB unchanged |
| `UC4-S16` | Document with violations across ≥3 WCAG criteria | `default` — diverse violations |
| `UC4-S17` | Document with Critical + Minor violations | `default` — known severity mapping |

### UI Actions Simulated

| Simulated Action | Playwright Mechanism |
|---|---|
| Click Check Accessibility | `page.click('#check-btn')` |
| Wait for results | `page.wait_for_selector('#summary-bar')` |
| Click Retry | `page.click('#retry-btn')` |
| Expand Critical group | `page.click('#critical-group .group-header')` |
| Expand Serious group | `page.click('#serious-group .group-header')` |
| Expand Minor group | `page.click('#minor-group .group-header')` |
| Read problem details | `page.text_content('.problem-card')` |
| Read summary counts | `page.text_content('#total-count')` |

### DB State Asserted

| Assertion | How |
|---|---|
| No new rows created (S14) | Count rows in `documents`, `document_versions`, `images` BEFORE and AFTER check — counts match |
| Multiple checks don't write (S15) | Run check 3 times, verify row counts unchanged |

### Metrics Recorded

| Metric | How | Used By |
|---|---|---|
| Scan latency | `time.time()` before Check → after results appear | S19 |
| Distinct WCAG criteria count | Count unique `rule_id` values in results | S16 |
| Severity classification | Compare `severity` field against expected for known violations | S17 |
| Rule citation accuracy | Compare `rule_id` + `rule_name` against WCAG spec | S18 |

### Step Definition Mapping

```
steps/uc4_steps.py
├── @given("the AccessibilityLead has loaded a valid document")       → DB seed + navigate
├── @given("the document contains accessibility problems")            → Seed problematic HTML
├── @given("the document has no accessibility problems")              → Seed clean HTML
├── @given("the document has no scannable content")                   → Seed empty doc
├── @given("no document is loaded in the session")                    → Skip document seed
├── @given("the document contains an image without alt text")         → Seed HTML with <img> no alt
├── @given("the document contains text with insufficient contrast")   → Seed HTML with low contrast
├── @given("the document has headings that skip levels")              → Seed HTML with h1→h3
├── @given("the document contains a form input without a label")      → Seed HTML with unlabeled input
├── @given("the accessibility scan service encounters an error")      → FakeChecker.error mode
├── @given("the AccessibilityLead has run a check and found problems")→ Check + verify results
├── @when('the AccessibilityLead clicks "Check Accessibility"')       → page.click('#check-btn')
├── @when("the AccessibilityLead fixes a problem in the document")    → Update document content
├── @when("the AccessibilityLead clicks \"Check Accessibility\" again")→ page.click('#check-btn')
├── @when("the AccessibilityLead tries to run a check")               → Attempt to click check
├── @when("the AccessibilityLead runs an accessibility check")        → Full check flow
├── @then("the system displays a list of accessibility problems")     → Assert problem cards visible
├── @then("the problems are grouped by severity: Critical, ...")      → Assert 3 severity groups
├── @then("each problem displays the WCAG rule ID and name")          → Assert .rule-id, .rule-name
├── @then("a summary bar shows the total number of problems")         → Assert #total-count visible
├── @then("the summary shows the count for each severity level")      → Assert severity badges
├── @then('a problem is reported for WCAG rule "1.1.1 ..."')          → Assert rule-id text
├── @then('the problem severity is "Critical"')                       → Assert parent group
├── @then("the problem includes the actual contrast ratio")           → Assert ratio in description
├── @then("the affected element is identified")                       → Assert .affected-element
├── @then("the fixed problem is no longer in the results")            → Assert problem absent
├── @then("the total problem count has decreased")                    → Compare counts
├── @then('the system displays a success message: "No ..."')          → Assert #no-issues-msg
├── @then("no problem list is shown")                                 → Assert no .problem-card
├── @then("the system displays a message indicating no content")      → Assert #empty-doc-msg
├── @then("the system displays an error message")                     → Assert #error-banner
├── @then('a "Retry" button is available')                            → Assert #retry-btn visible
├── @then("a scanning indicator is shown")                            → Assert #scanning-indicator
├── @then("the indicator disappears when results are ready")          → Assert indicator hidden
├── @then("the system prompts the user to load a document first")     → Assert #no-doc-msg
├── @then("the database row count remains unchanged")                 → DB count comparison
├── @then("no new records are created")                               → DB count comparison
├── @then("the database remains unchanged after all three checks")    → DB count comparison
├── @then("the results include violations from at least 3 ...")       → Count distinct rule_id
├── @then('the missing alt text is classified as "Critical"')         → Assert severity
├── @then("the contrast problem cites WCAG rule \"1.4.3\"")           → Assert rule-id text
├── @then("the results appear within 15 seconds")                    → Timing check
└── @then("each problem identifies the affected element or text")     → Assert .affected-element
```

---

## E) Traceability Table

| Scenario ID | Category | UI Elements | DB Elements | Service Elements |
|---|---|---|---|---|
| UC4-S01 | Happy path | `check-btn`, `summary-bar`, severity groups, `problem-card` | — (read only) | `AccessibilityCheckerPort.scan()` |
| UC4-S02 | Happy path | `problem-card` → `rule-id`, `rule-name`, `problem-description` | — | `scan()` → `AccessibilityProblem` |
| UC4-S03 | Happy path | `summary-bar`, `total-count`, severity badges | — | `scan()` → `AccessibilityReport.summary` |
| UC4-S04 | Happy path | `problem-card` with `rule-id`="1.1.1", `critical-group` | `images.alt_text` IS NULL (input) | `scan()` detects missing alt |
| UC4-S05 | Happy path | `problem-card` with `rule-id`="1.4.3", contrast ratio in description | — | `scan()` detects low contrast |
| UC4-S06 | Happy path | `problem-card` with heading violation, `serious-group` or `minor-group` | — | `scan()` detects skipped headings |
| UC4-S07 | Happy path | `problem-card` with `rule-id`="1.3.1", `affected-element` | — | `scan()` detects unlabeled input |
| UC4-S08 | Happy path | `check-btn` (×2), `total-count` decreased, problem removed | Document content updated | `scan()` ×2, compare results |
| UC4-S09 | Negative | `no-issues-msg`, no `problem-card` | — | `scan()` → empty list |
| UC4-S10 | Negative | `empty-doc-msg` | — | `check_document()` → empty-doc error |
| UC4-S11 | Negative | `error-banner`, `retry-btn` | — | `scan()` → exception |
| UC4-S12 | Negative | `scanning-indicator` (visible then hidden) | — | `scan()` (timing) |
| UC4-S13 | Negative | `no-doc-msg` | No document row | — (validation) |
| UC4-S14 | Persistence | `check-btn` | Row counts unchanged | `scan()` (read-only verified) |
| UC4-S15 | Persistence | `check-btn` (×3) | Row counts unchanged after 3 checks | `scan()` ×3 (read-only verified) |
| UC4-S16 | Quality | `problem-card` (multiple), distinct `rule-id` ≥3 | — | `scan()` → diverse violations |
| UC4-S17 | Quality | `critical-group` has alt text issue, `minor-group` has heading issue | — | `scan()` → severity mapping |
| UC4-S18 | Quality | `rule-id`="1.4.3", `rule-name` contains "Contrast" | — | `scan()` → citation accuracy |
| UC4-S19 | Quality | Results visible within 15s of clicking check | — | `scan()` → latency ≤ 15s |
| UC4-S20 | Quality | `affected-element` visible in each `problem-card` | — | `scan()` → element identification |
