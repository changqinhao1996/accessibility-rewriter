/**
 * RewritePage — UC1: RewriteTextToReadingLevel
 *
 * Single-page component implementing the state machine:
 *   idle → loading → reviewing → saving → idle
 *   idle → error → idle
 *
 * All HTML element IDs match the UC1 UI Design Spec exactly.
 */

import { useCallback, useEffect, useState } from "react";
import { rewriteText, saveVersion, getDocument } from "../services/rewriteApi";
import { READING_LEVELS } from "../types/rewrite";
import type { RewriteResult, DocumentOut } from "../types/rewrite";
import "./RewritePage.css";

type PageState = "idle" | "loading" | "reviewing" | "saving" | "error";

interface ErrorInfo {
  type: "empty-text" | "no-level" | "unclear-text" | "service-unavailable";
  message: string;
}

// The document ID is loaded from the first available document.
// In acceptance tests, this is seeded via the database.
const DEMO_DOCUMENT_ID = import.meta.env.VITE_DOCUMENT_ID || "";

export default function RewritePage() {
  // ── State ──────────────────────────────────────────────────────────
  const [document, setDocument] = useState<DocumentOut | null>(null);
  const [sourceText, setSourceText] = useState("");
  const [readingLevel, setReadingLevel] = useState("");
  const [pageState, setPageState] = useState<PageState>("idle");
  const [rewriteResult, setRewriteResult] = useState<RewriteResult | null>(null);
  const [error, setError] = useState<ErrorInfo | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  // ── Load document on mount ─────────────────────────────────────────
  useEffect(() => {
    if (!DEMO_DOCUMENT_ID) return;

    getDocument(DEMO_DOCUMENT_ID)
      .then((doc) => {
        setDocument(doc);
        setSourceText(doc.content);
      })
      .catch(() => {
        // No document loaded — controls stay disabled (S05)
        setDocument(null);
      });
  }, []);

  const isDocumentLoaded = document !== null;

  // ── Validation helpers ─────────────────────────────────────────────
  const isTextEmpty = !sourceText || !sourceText.trim();
  const isLevelSelected = readingLevel !== "";
  const canSubmit = isDocumentLoaded && !isTextEmpty && isLevelSelected;

  // ── Handlers ───────────────────────────────────────────────────────
  const handleRewrite = useCallback(async () => {
    // Client-side validation (mirrors server-side for immediate feedback)
    if (isTextEmpty) {
      setError({
        type: "empty-text",
        message: "Please enter or select source text before rewriting.",
      });
      setPageState("error");
      return;
    }
    if (!isLevelSelected) {
      setError({
        type: "no-level",
        message: "Please select a target reading level.",
      });
      setPageState("error");
      return;
    }

    setPageState("loading");
    setError(null);
    setSuccessMessage(null);

    try {
      const result = await rewriteText(sourceText, readingLevel);
      setRewriteResult(result);
      setPageState("reviewing");
    } catch (err: any) {
      const status = err.status;
      const detail = err.detail || err.message;

      if (status === 422) {
        // Determine which validation error
        if (detail.toLowerCase().includes("source text") || detail.toLowerCase().includes("empty")) {
          setError({ type: "empty-text", message: detail });
        } else {
          setError({ type: "no-level", message: detail });
        }
      } else if (status === 502) {
        setError({
          type: "unclear-text",
          message: detail || "The text is too unclear to rewrite safely. Please revise the source text and try again.",
        });
      } else if (status === 503) {
        setError({
          type: "service-unavailable",
          message: detail || "The rewriting service is currently unavailable. Please try again shortly.",
        });
      } else {
        setError({
          type: "service-unavailable",
          message: detail || "An unexpected error occurred.",
        });
      }
      setPageState("error");
    }
  }, [sourceText, readingLevel, isTextEmpty, isLevelSelected]);

  const handleSave = useCallback(async () => {
    if (!rewriteResult || !document) return;

    setIsSaving(true);
    try {
      const version = await saveVersion(
        document.id,
        rewriteResult.rewritten_text,
        rewriteResult.target_reading_level,
        "ContentDesigner" // Hardcoded author per A8 (auth handled outside UC1)
      );
      setSuccessMessage(`Draft saved as version ${version.version_number}.`);
      setRewriteResult(null);
      setPageState("idle");
    } catch {
      setError({
        type: "service-unavailable",
        message: "Failed to save the version. Please try again.",
      });
      setPageState("error");
    } finally {
      setIsSaving(false);
    }
  }, [rewriteResult, document]);

  const handleDiscard = useCallback(() => {
    setRewriteResult(null);
    setError(null);
    setSuccessMessage(null);
    setPageState("idle");
  }, []);

  const handleRetry = useCallback(() => {
    setError(null);
    setPageState("idle");
  }, []);

  const handleDismissSuccess = useCallback(() => {
    setSuccessMessage(null);
  }, []);

  // ── Render ─────────────────────────────────────────────────────────
  return (
    <div className="rewrite-page">
      <header className="rewrite-header">
        <h1>Rewrite Text to Reading Level</h1>
      </header>

      {/* ── Success Toast ─────────────────────────────────────────── */}
      {successMessage && (
        <div id="toast-success" role="alert" className="toast toast-success">
          <span>{successMessage}</span>
          <button
            type="button"
            className="toast-dismiss"
            onClick={handleDismissSuccess}
            aria-label="Dismiss"
          >
            ×
          </button>
        </div>
      )}

      {/* ── Error Messages ────────────────────────────────────────── */}
      {error?.type === "empty-text" && (
        <div id="error-empty-text" className="error-banner" role="alert">
          {error.message}
        </div>
      )}
      {error?.type === "no-level" && (
        <div id="error-no-level" className="error-banner" role="alert">
          {error.message}
        </div>
      )}
      {error?.type === "unclear-text" && (
        <div id="error-unclear-text" className="error-banner error-danger" role="alert">
          {error.message}
        </div>
      )}
      {error?.type === "service-unavailable" && (
        <div id="error-service-unavailable" className="error-banner error-danger" role="alert">
          <span>{error.message}</span>
          <button id="btn-retry" type="button" className="btn btn-retry" onClick={handleRetry}>
            Retry
          </button>
        </div>
      )}

      {/* ── Input Controls ────────────────────────────────────────── */}
      <div className="input-section">
        <label htmlFor="source-text" className="label">
          Source Text
        </label>
        <textarea
          id="source-text"
          className="source-textarea"
          value={sourceText}
          onChange={(e) => setSourceText(e.target.value)}
          disabled={!isDocumentLoaded}
          placeholder={isDocumentLoaded ? "Enter or select text to rewrite…" : "No document loaded"}
          rows={8}
        />

        <div className="controls-row">
          <div className="select-wrapper">
            <label htmlFor="reading-level-select" className="label">
              Target Reading Level
            </label>
            <select
              id="reading-level-select"
              className="level-select"
              value={readingLevel}
              onChange={(e) => setReadingLevel(e.target.value)}
              disabled={!isDocumentLoaded}
            >
              <option value="">Choose a level…</option>
              {READING_LEVELS.map((level) => (
                <option key={level.label} value={level.label}>
                  {level.label}
                </option>
              ))}
            </select>
          </div>

          <button
            id="btn-rewrite"
            type="button"
            className="btn btn-primary"
            onClick={handleRewrite}
            disabled={!canSubmit || pageState === "loading"}
          >
            {pageState === "loading" ? "Rewriting…" : "Rewrite"}
          </button>
        </div>
      </div>

      {/* ── Side-by-side Comparison ───────────────────────────────── */}
      {pageState === "reviewing" && rewriteResult && (
        <div className="comparison-section">
          <div className="comparison-panels">
            <div className="panel">
              <h2 className="panel-heading">Original</h2>
              <div id="panel-original" className="panel-content">
                {rewriteResult.original_text}
              </div>
            </div>
            <div className="panel">
              <h2 className="panel-heading">
                Rewritten
                <span className="grade-badge">
                  Grade {rewriteResult.reading_grade.toFixed(1)}
                </span>
              </h2>
              <div id="panel-rewritten" className="panel-content">
                {rewriteResult.rewritten_text}
              </div>
            </div>
          </div>

          <div className="action-row">
            <button
              id="btn-save"
              type="button"
              className="btn btn-success"
              onClick={handleSave}
              disabled={isSaving}
            >
              {isSaving ? "Saving…" : "Save Draft"}
            </button>
            <button
              id="btn-discard"
              type="button"
              className="btn btn-secondary"
              onClick={handleDiscard}
            >
              Discard
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
