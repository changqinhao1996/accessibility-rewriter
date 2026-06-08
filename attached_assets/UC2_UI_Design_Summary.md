# UC2 — UI Design Summary: MeasureReadingLevel

## Page / Component: ReadabilityPanel

UC2 does **not** require a new page. It adds a **ReadabilityPanel** component to the existing editor area (alongside the UC1 RewritePage), activated when the ContentDesigner selects text.

---

## Component Hierarchy

```
RewritePage (existing)
└── ReadabilityPanel (new — UC2)
    ├── EmptyState          — "Select text to measure reading level"
    ├── WarningState        — "Selection too short for meaningful analysis"
    ├── ReadabilityBadge    — Grade + Level Name (always visible when valid)
    │   └── DetailsToggle   — "Show Details" / "Hide Details" button
    └── BreakdownPanel      — Collapsible detailed view
        ├── GradeDisplay    — Reading-level name + numeric grade
        ├── HighlightedText — Passage with complex words & long sentences marked
        └── Legend           — Color key for word vs sentence highlights
```

---

## UI Elements Inventory

| Element ID | Type | Visible When | Content / Behavior |
|---|---|---|---|
| `readability-panel` | Container | Always | Wrapper for the readability measurement area |
| `readability-empty` | Text prompt | No selection or whitespace-only | "Select text to measure reading level" |
| `readability-warning` | Warning banner | Selection is a single word | "Selection too short for meaningful analysis" |
| `readability-badge` | Badge/pill | Valid selection (≥2 words, non-whitespace) | Shows grade number + level name |
| `readability-grade` | Span inside badge | Badge visible | Numeric Flesch–Kincaid grade (e.g., "11.9") |
| `readability-level-name` | Span inside badge | Badge visible | Level name (e.g., "Standard (Grades 9–12)") |
| `details-toggle` | Button | Badge visible | Toggles "Show Details" ↔ "Hide Details" |
| `breakdown-panel` | Collapsible div | Toggle is open | Full passage with highlights |
| `breakdown-grade` | Heading | Breakdown open | Repeats grade + level name |
| `highlight-word` | `<mark>` tag | Breakdown open | Complex word (≥3 syllables), styled with `--word-highlight` color |
| `highlight-sentence` | `<span>` wrapper | Breakdown open | Long sentence (above average word count), styled with `--sentence-highlight` background |

---

## Visual Design

- **Badge**: Matches the existing `grade-badge` style from UC1 — pill shape, purple tint
- **Word highlights**: Orange/amber underline + slight bold — `color: #d29922; text-decoration: underline wavy`
- **Sentence highlights**: Light yellow background tint — `background: rgba(210, 153, 34, 0.08)`
- **Empty/Warning states**: Follow existing `error-banner` pattern from UC1

---

## State Machine

```
┌───────────┐  select text   ┌──────────────┐   click "Show Details"   ┌─────────────────┐
│ empty     │ ──────────────→│ badge-shown  │──────────────────────────→│ breakdown-open  │
│ (no       │                │ (grade +     │                           │ (grade + level  │
│  selection)│←──────────────│  level name) │←──────────────────────────│  + highlights)  │
└───────────┘  clear select  └──────────────┘   click "Hide Details"   └─────────────────┘
      ↑                            │
      │    single word /           │  change selection
      │    whitespace              │  (recalculate)
      ↓                            ↓
┌───────────┐               ┌──────────────┐
│ warning   │               │ badge-shown  │
│ (too short)│              │ (new grade)  │
└───────────┘               └──────────────┘
```
