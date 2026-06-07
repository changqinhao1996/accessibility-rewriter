# A) UI Design Summary

## UC1 — RewriteTextToReadingLevel

### Screen: RewritePage

A single page accessible when a document is loaded. It transitions through three states:

```
[Initial] ──document loaded──▶ Idle
Idle ──rewrite response received──▶ Reviewing
Reviewing ──discard──▶ Idle
Reviewing ──save confirmed──▶ Saved
Idle ──validation / service error──▶ Error
Reviewing ──service error──▶ Error
Error ──dismiss / retry──▶ Idle
Saved ──new session──▶ Idle
```

---

### Inputs

| Element | Type | HTML `id` | Behaviour | Scenarios |
|---|---|---|---|---|
| Source text area | `<textarea>` | `source-text` | Pre-filled with document text; user may select a portion. Disabled when no document is loaded. | S01–S04, S06–S09 |
| Reading-level selector | `<select>` | `reading-level-select` | Dropdown with options: "Plain (Grades 6–8)", "Simple (Grades 3–5)", etc. Default: no selection (placeholder "Choose a level…"). Disabled when no document is loaded. | S01–S04, S06–S08 |
| Rewrite button | `<button>` | `btn-rewrite` | Submits the rewrite request. **Disabled** when: (a) no document loaded, (b) source text is empty/whitespace, or (c) no reading level selected. | S01–S10, S16, S17 |
| Save button | `<button>` | `btn-save` | Visible only in Reviewing state. Persists the draft as a new version. | S02, S12, S13 |
| Discard button | `<button>` | `btn-discard` | Visible only in Reviewing state. Discards the draft and returns to Idle. | S11, S14 |
| Retry button | `<button>` | `btn-retry` | Visible only when a service-unavailable error is displayed. | S10 |

---

### Outputs / Results

| Element | Type | HTML `id` | Content | Scenarios |
|---|---|---|---|---|
| Original text panel | `<div>` | `panel-original` | Shows the original source text (read-only). Visible in Reviewing state. | S01–S04 |
| Rewritten text panel | `<div>` | `panel-rewritten` | Shows the AI-rewritten text. Visible in Reviewing state. | S01–S04, S12, S17 |
| Success toast | `<div role="alert">` | `toast-success` | "Draft saved as version N." Visible after save. | S02 |

---

### Errors / Messages

| Element | HTML `id` | Message | Trigger | Scenarios |
|---|---|---|---|---|
| Validation error: empty text | `error-empty-text` | "Please enter or select source text before rewriting." | Submit with empty/whitespace text | S06, S07 |
| Validation error: no level | `error-no-level` | "Please select a target reading level." | Submit without level selected | S08 |
| Error: unclear text | `error-unclear-text` | "The text is too unclear to rewrite safely. Please revise the source text and try again." | StyleRewriter returns unclear-text error | S09 |
| Error: service unavailable | `error-service-unavailable` | "The rewriting service is currently unavailable. Please try again shortly." | StyleRewriter unreachable / 5xx | S10 |

---

### Disabled-state Rules (Precondition)

| Condition | Disabled elements | Scenario |
|---|---|---|
| No document loaded | `source-text`, `reading-level-select`, `btn-rewrite` — all disabled | S05 |
