/**
 * ReadabilityService — Pure TypeScript Flesch-Kincaid readability analysis.
 * UC2: MeasureReadingLevel
 *
 * All functions are pure and synchronous — no API calls, no side effects.
 * Designed to run in <1ms for typical passages (meets 200ms SLA easily).
 */

import { READING_LEVELS } from "../types/rewrite";

// ── Types ────────────────────────────────────────────────────────────

export interface ReadabilityResult {
  grade: number;
  levelName: string;
}

export interface ComplexWord {
  word: string;
  syllables: number;
  startIndex: number;
  endIndex: number;
}

export interface LongSentence {
  sentence: string;
  wordCount: number;
  startIndex: number;
  endIndex: number;
}

export interface ReadabilityBreakdown {
  result: ReadabilityResult;
  complexWords: ComplexWord[];
  longSentences: LongSentence[];
  averageSentenceLength: number;
  totalWords: number;
  totalSentences: number;
}

// ── Syllable Counter ─────────────────────────────────────────────────

/**
 * Count syllables in a word using a heuristic algorithm.
 * Based on the English syllable counting rules used by readability formulas.
 */
export function countSyllables(word: string): number {
  const w = word.toLowerCase().replace(/[^a-z]/g, "");
  if (w.length <= 2) return 1;

  let count = 0;
  const vowels = "aeiouy";
  let prevVowel = false;

  for (let i = 0; i < w.length; i++) {
    const isVowel = vowels.includes(w[i]);
    if (isVowel && !prevVowel) {
      count++;
    }
    prevVowel = isVowel;
  }

  // Subtract silent 'e' at end
  if (w.endsWith("e") && count > 1) {
    count--;
  }

  // Handle special endings
  if (w.endsWith("le") && w.length > 2 && !vowels.includes(w[w.length - 3])) {
    count++;
  }

  return Math.max(count, 1);
}

// ── Text Tokenization ────────────────────────────────────────────────

/**
 * Split text into sentences. Handles ., !, ? as delimiters.
 */
function splitSentences(text: string): string[] {
  return text
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
}

/**
 * Split text into words (alphanumeric tokens).
 */
function splitWords(text: string): string[] {
  return text.match(/[a-zA-Z]+(?:['-][a-zA-Z]+)*/g) || [];
}

// ── Flesch-Kincaid Grade Level ───────────────────────────────────────

/**
 * Compute the Flesch-Kincaid Grade Level for a passage of text.
 *
 * Formula: 0.39 × (words/sentences) + 11.8 × (syllables/words) − 15.59
 *
 * Returns a number representing the U.S. school grade level.
 */
export function fleschKincaidGrade(text: string): number {
  const words = splitWords(text);
  const sentences = splitSentences(text);

  if (words.length === 0 || sentences.length === 0) return 0;

  const totalSyllables = words.reduce((sum, w) => sum + countSyllables(w), 0);
  const avgWordsPerSentence = words.length / sentences.length;
  const avgSyllablesPerWord = totalSyllables / words.length;

  const grade =
    0.39 * avgWordsPerSentence + 11.8 * avgSyllablesPerWord - 15.59;

  return Math.round(grade * 100) / 100; // 2 decimal places
}

// ── Grade → Level Name Mapping ───────────────────────────────────────

/**
 * Map a Flesch-Kincaid grade to a reading-level name.
 * Uses the same 5-tier taxonomy as UC1.
 */
export function mapGradeToLevel(grade: number): string {
  if (grade <= 3) return READING_LEVELS[0].label; // Very Simple (Grades 1–3)
  if (grade <= 5) return READING_LEVELS[1].label; // Simple (Grades 4–5)
  if (grade <= 8) return READING_LEVELS[2].label; // Plain (Grades 6–8)
  if (grade <= 12) return READING_LEVELS[3].label; // Standard (Grades 9–12)
  return READING_LEVELS[4].label; // Technical (Grade 13+)
}

// ── Complex Words ────────────────────────────────────────────────────

/**
 * Find all words with ≥3 syllables and their positions in the text.
 */
export function getComplexWords(text: string): ComplexWord[] {
  const results: ComplexWord[] = [];
  const regex = /[a-zA-Z]+(?:['-][a-zA-Z]+)*/g;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(text)) !== null) {
    const word = match[0];
    const syllables = countSyllables(word);
    if (syllables >= 3) {
      results.push({
        word,
        syllables,
        startIndex: match.index,
        endIndex: match.index + word.length,
      });
    }
  }

  return results;
}

// ── Long Sentences ───────────────────────────────────────────────────

/**
 * Find sentences whose word count is above the passage average.
 */
export function getLongSentences(text: string): LongSentence[] {
  const sentences = splitSentences(text);
  if (sentences.length === 0) return [];

  const wordCounts = sentences.map((s) => splitWords(s).length);
  const avgWordCount =
    wordCounts.reduce((a, b) => a + b, 0) / wordCounts.length;

  const results: LongSentence[] = [];
  let searchFrom = 0;

  for (let i = 0; i < sentences.length; i++) {
    const sentence = sentences[i];
    const wc = wordCounts[i];
    const startIndex = text.indexOf(sentence, searchFrom);

    if (wc > avgWordCount) {
      results.push({
        sentence,
        wordCount: wc,
        startIndex,
        endIndex: startIndex + sentence.length,
      });
    }

    searchFrom = startIndex + sentence.length;
  }

  return results;
}

// ── Full Analysis Orchestrator ───────────────────────────────────────

/**
 * Perform a complete readability analysis on the given text.
 *
 * Returns null if the text is too short for meaningful analysis (< 2 words).
 */
export function analyzeText(text: string): ReadabilityBreakdown | null {
  const trimmed = text.trim();
  if (!trimmed) return null;

  const words = splitWords(trimmed);
  if (words.length < 2) return null; // Too short

  const sentences = splitSentences(trimmed);
  const grade = fleschKincaidGrade(trimmed);
  const levelName = mapGradeToLevel(grade);
  const complexWords = getComplexWords(trimmed);
  const longSentences = getLongSentences(trimmed);

  const totalWords = words.length;
  const totalSentences = sentences.length;
  const averageSentenceLength =
    totalSentences > 0 ? totalWords / totalSentences : 0;

  return {
    result: { grade, levelName },
    complexWords,
    longSentences,
    averageSentenceLength,
    totalWords,
    totalSentences,
  };
}
