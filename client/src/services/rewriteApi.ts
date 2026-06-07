/**
 * API client functions for UC1: RewriteTextToReadingLevel.
 */

import type {
  DocumentOut,
  RewriteRequest,
  RewriteResult,
  SaveVersionRequest,
  VersionOut,
} from "../types/rewrite";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

/**
 * Generic fetch wrapper that throws with the server's error detail on failure.
 */
async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    const error = new Error(body.detail || `HTTP ${res.status}`);
    (error as any).status = res.status;
    (error as any).detail = body.detail;
    throw error;
  }

  return res.json() as Promise<T>;
}

/** POST /api/rewrite */
export async function rewriteText(
  text: string,
  readingLevel: string
): Promise<RewriteResult> {
  const body: RewriteRequest = { text, reading_level: readingLevel };
  return apiFetch<RewriteResult>("/rewrite", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** GET /api/documents/{id} */
export async function getDocument(documentId: string): Promise<DocumentOut> {
  return apiFetch<DocumentOut>(`/documents/${documentId}`);
}

/** GET /api/documents/{id}/versions */
export async function getVersions(documentId: string): Promise<VersionOut[]> {
  return apiFetch<VersionOut[]>(`/documents/${documentId}/versions`);
}

/** POST /api/documents/{id}/versions */
export async function saveVersion(
  documentId: string,
  content: string,
  readingLevel: string,
  author: string
): Promise<VersionOut> {
  const body: SaveVersionRequest = {
    content,
    reading_level: readingLevel,
    author,
  };
  return apiFetch<VersionOut>(`/documents/${documentId}/versions`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
