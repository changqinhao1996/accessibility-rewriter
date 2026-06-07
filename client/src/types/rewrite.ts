/**
 * TypeScript types matching the server API schemas.
 * UC1: RewriteTextToReadingLevel
 */

export interface RewriteRequest {
  text: string;
  reading_level: string;
}

export interface RewriteResult {
  original_text: string;
  rewritten_text: string;
  reading_grade: number;
  target_reading_level: string;
}

export interface DocumentOut {
  id: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface VersionOut {
  id: string;
  document_id: string;
  version_number: number;
  content: string;
  reading_level: string;
  author: string;
  created_at: string;
}

export interface SaveVersionRequest {
  content: string;
  reading_level: string;
  author: string;
}

/** Available reading levels with their labels and target grade midpoints. */
export const READING_LEVELS = [
  { label: "Very Simple (Grades 1–3)", midpoint: 2 },
  { label: "Simple (Grades 4–5)", midpoint: 4.5 },
  { label: "Plain (Grades 6–8)", midpoint: 7 },
  { label: "Standard (Grades 9–12)", midpoint: 10.5 },
  { label: "Technical (Grade 13+)", midpoint: 14 },
] as const;

export type ReadingLevelLabel = (typeof READING_LEVELS)[number]["label"];

/** API error response shape. */
export interface ApiError {
  detail: string;
}
