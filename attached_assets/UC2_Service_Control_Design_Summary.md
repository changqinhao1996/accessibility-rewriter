# UC2 — Service / Control Design Summary: MeasureReadingLevel

## Key Design Decision: Client-Side Computation

Unlike UC1 (which calls Claude via the server), UC2's readability analysis is **purely algorithmic** (Assumption A5). The Flesch–Kincaid formula is simple enough to run client-side in <1ms, easily meeting the 200ms SLA (QR-1). A server endpoint is added as a fallback/for testing.

---

## Service: `ReadabilityService` (TypeScript — client-side)

```
ReadabilityService
├── analyzeText(text: string) → ReadabilityResult
│   ├── Compute Flesch–Kincaid grade level
│   ├── Map grade to reading-level name
│   └── Return { grade, levelName }
├── getComplexWords(text: string) → ComplexWord[]
│   └── Return words with ≥3 syllables + their positions
├── getLongSentences(text: string) → LongSentence[]
│   └── Return sentences with word count > passage average
└── countSyllables(word: string) → number
    └── Heuristic syllable counter
```

---

## Types

```typescript
interface ReadabilityResult {
  grade: number;             // Flesch–Kincaid grade level (e.g., 11.9)
  levelName: string;         // "Standard (Grades 9–12)"
}

interface ComplexWord {
  word: string;              // The raw word
  syllables: number;         // Syllable count
  startIndex: number;        // Position in text
  endIndex: number;
}

interface LongSentence {
  sentence: string;          // The raw sentence
  wordCount: number;         // Word count
  startIndex: number;        // Position in text
  endIndex: number;
}

interface ReadabilityBreakdown {
  result: ReadabilityResult;
  complexWords: ComplexWord[];
  longSentences: LongSentence[];
  averageSentenceLength: number;
}
```

---

## Grade → Level Name Mapping

Reuses the same `READING_LEVELS` array from UC1 types:

| Grade (g) | Level Name |
|---|---|
| g ≤ 3 | Very Simple (Grades 1–3) |
| 3 < g ≤ 5 | Simple (Grades 4–5) |
| 5 < g ≤ 8 | Plain (Grades 6–8) |
| 8 < g ≤ 12 | Standard (Grades 9–12) |
| g > 12 | Technical (Grade 13+) |

---

## Validation Rules

| Condition | Behavior |
|---|---|
| No selection / whitespace-only | Show empty state prompt |
| Selection is a single word | Show warning ("too short") |
| Selection ≥ 2 words | Compute and display score |

---

## API Endpoint: `POST /api/analyze` (Backend — for testing)

A lightweight backend endpoint mirrors the client-side logic to enable server-side acceptance tests:

```
POST /api/analyze
Body: { "text": "..." }
Response 200: {
  "grade": 11.9,
  "level_name": "Standard (Grades 9–12)",
  "complex_words": [...],
  "long_sentences": [...],
  "average_sentence_length": 18.5
}
Response 422: { "detail": "Text too short for analysis" }
```

---

## External Dependencies

| Dependency | UC2 Usage |
|---|---|
| `textstat` (Python) | Server-side Flesch–Kincaid (already installed for UC1) |
| Custom syllable counter (TypeScript) | Client-side syllable heuristic (no npm dependency needed) |
| **No AI / no StyleRewriter** | UC2 is entirely algorithmic |

---

## Integration with UC1

| Aspect | How UC2 Integrates |
|---|---|
| Shared types | Reuses `READING_LEVELS` from `client/src/types/rewrite.ts` |
| Shared UI | ReadabilityPanel renders inside the existing RewritePage layout |
| Shared seed data | Same photosynthesis document used in both use cases |
| Independent operation | UC2 does not call the `/api/rewrite` endpoint or use StyleRewriter |
