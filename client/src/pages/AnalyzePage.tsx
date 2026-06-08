/**
 * AnalyzePage — UC2: MeasureReadingLevel
 *
 * Dedicated page for real-time Flesch-Kincaid readability analysis.
 * The user types/pastes text, clicks "Analyze", and sees the grade,
 * level name, and a detailed breakdown with highlighted complex words
 * and long sentences.
 */

import { useCallback, useState } from "react";
import {
  analyzeText,
  type ReadabilityBreakdown,
} from "../services/readabilityService";
import "./AnalyzePage.css";

type PageState = "empty" | "warning" | "badge" | "breakdown";

export default function AnalyzePage() {
  const [text, setText] = useState(
    "Photosynthesis is the biochemical process by which chloroplasts in plant cells " +
      "convert light energy into adenosine triphosphate, facilitating the synthesis of " +
      "glucose from carbon dioxide and water. The chlorophyll pigments within the " +
      "thylakoid membranes absorb photon energy, initiating a cascade of electron " +
      "transfer reactions that ultimately reduce NADP+ to NADPH."
  );
  const [analysis, setAnalysis] = useState<ReadabilityBreakdown | null>(null);
  const [pageState, setPageState] = useState<PageState>("empty");

  // ── Analyze ──────────────────────────────────────────────────────────

  const handleAnalyze = useCallback(() => {
    const trimmed = text.trim();

    if (!trimmed) {
      setAnalysis(null);
      setPageState("empty");
      return;
    }

    // Check for single word
    const wordCount = (
      trimmed.match(/[a-zA-Z]+(?:['-][a-zA-Z]+)*/g) || []
    ).length;
    if (wordCount < 2) {
      setAnalysis(null);
      setPageState("warning");
      return;
    }

    const result = analyzeText(trimmed);
    if (!result) {
      setPageState("warning");
      return;
    }

    setAnalysis(result);
    setPageState("badge");
  }, [text]);

  const handleShowDetails = () => setPageState("breakdown");
  const handleHideDetails = () => setPageState("badge");

  const handleClear = () => {
    setAnalysis(null);
    setPageState("empty");
  };

  // ── Render Highlighted Text ──────────────────────────────────────────

  const renderHighlightedText = (breakdown: ReadabilityBreakdown) => {
    const { complexWords, longSentences } = breakdown;
    const src = text.trim();

    // Build a set of character ranges for complex words
    const wordRanges = new Set<number>();
    for (const cw of complexWords) {
      for (let i = cw.startIndex; i < cw.endIndex; i++) {
        wordRanges.add(i);
      }
    }

    // Build a set of character ranges for long sentences
    const sentenceRanges = new Set<number>();
    for (const ls of longSentences) {
      for (let i = ls.startIndex; i < ls.endIndex; i++) {
        sentenceRanges.add(i);
      }
    }

    // Render character by character with spans
    const elements: React.ReactNode[] = [];
    let i = 0;

    while (i < src.length) {
      // Check for complex word start
      const cw = complexWords.find((w) => w.startIndex === i);
      if (cw) {
        const isInLongSentence = sentenceRanges.has(i);
        elements.push(
          <mark
            key={`w-${i}`}
            className={`highlight-word ${isInLongSentence ? "in-long-sentence" : ""}`}
            title={`${cw.syllables} syllables`}
          >
            {src.slice(cw.startIndex, cw.endIndex)}
          </mark>
        );
        i = cw.endIndex;
        continue;
      }

      // Check for long sentence start (only for non-word characters)
      const ls = longSentences.find(
        (s) => s.startIndex === i && !wordRanges.has(i)
      );
      if (ls) {
        // Render the sentence with highlights for embedded complex words
        const sentenceText = src.slice(ls.startIndex, ls.endIndex);
        const innerElements: React.ReactNode[] = [];
        let j = 0;

        while (j < sentenceText.length) {
          const innerCw = complexWords.find(
            (w) => w.startIndex === ls.startIndex + j
          );
          if (innerCw) {
            innerElements.push(
              <mark
                key={`sw-${ls.startIndex}-${j}`}
                className="highlight-word in-long-sentence"
                title={`${innerCw.syllables} syllables`}
              >
                {sentenceText.slice(j, j + (innerCw.endIndex - innerCw.startIndex))}
              </mark>
            );
            j += innerCw.endIndex - innerCw.startIndex;
          } else {
            innerElements.push(sentenceText[j]);
            j++;
          }
        }

        elements.push(
          <span key={`s-${i}`} className="highlight-sentence">
            {innerElements}
          </span>
        );
        i = ls.endIndex;
        continue;
      }

      // Regular character
      elements.push(src[i]);
      i++;
    }

    return <div className="highlighted-text">{elements}</div>;
  };

  // ── Render ─────────────────────────────────────────────────────────

  return (
    <div className="analyze-page">
      <header className="analyze-header">
        <h1>Measure Reading Level</h1>
      </header>

      {/* ── Editor ──────────────────────────────────────────────── */}
      <section className="input-section">
        <label className="label" htmlFor="analyze-editor">
          Text to Analyze
        </label>
        <textarea
          id="analyze-editor"
          className="source-textarea"
          rows={8}
          value={text}
          onChange={(e) => {
            setText(e.target.value);
            // Reset analysis when text changes
            if (pageState !== "empty") {
              handleClear();
            }
          }}
          placeholder="Paste or type text here to measure its reading level…"
        />
        <div className="controls-row">
          <button
            id="analyze-btn"
            className="btn btn-primary"
            onClick={handleAnalyze}
            disabled={!text.trim()}
          >
            📊 Analyze
          </button>
          {analysis && (
            <button className="btn btn-secondary" onClick={handleClear}>
              Clear
            </button>
          )}
        </div>
      </section>

      {/* ── Readability Panel ───────────────────────────────────── */}
      <div id="readability-panel" className="readability-panel">
        {/* Empty State */}
        {pageState === "empty" && (
          <div id="readability-empty" className="readability-empty">
            Select text to measure reading level
          </div>
        )}

        {/* Warning State */}
        {pageState === "warning" && (
          <div id="readability-warning" className="readability-warning">
            ⚠️ Selection too short for meaningful analysis
          </div>
        )}

        {/* Badge State */}
        {(pageState === "badge" || pageState === "breakdown") && analysis && (
          <>
            <div id="readability-badge" className="readability-badge">
              <div className="badge-content">
                <span className="badge-icon">📊</span>
                <span id="readability-level-name" className="badge-level">
                  {analysis.result.levelName}
                </span>
                <span id="readability-grade" className="badge-grade">
                  Grade {analysis.result.grade}
                </span>
              </div>
              <div className="badge-stats">
                <span>{analysis.totalWords} words</span>
                <span>{analysis.totalSentences} sentences</span>
                <span>
                  Avg {analysis.averageSentenceLength.toFixed(1)} words/sentence
                </span>
              </div>
              <button
                id="details-toggle"
                className="btn btn-secondary btn-small"
                onClick={
                  pageState === "breakdown"
                    ? handleHideDetails
                    : handleShowDetails
                }
              >
                {pageState === "breakdown" ? "Hide Details" : "Show Details"}
              </button>
            </div>

            {/* Breakdown Panel */}
            {pageState === "breakdown" && (
              <div id="breakdown-panel" className="breakdown-panel">
                <div className="breakdown-header">
                  <h3>
                    Detailed Breakdown —{" "}
                    <span className="breakdown-level">
                      {analysis.result.levelName}
                    </span>{" "}
                    ·{" "}
                    <span className="breakdown-grade">
                      Grade {analysis.result.grade}
                    </span>
                  </h3>
                </div>

                <div className="breakdown-legend">
                  <span className="legend-item">
                    <mark className="highlight-word legend-swatch">word</mark>{" "}
                    Complex word (≥3 syllables) —{" "}
                    {analysis.complexWords.length} found
                  </span>
                  <span className="legend-item">
                    <span className="highlight-sentence legend-swatch">
                      sentence
                    </span>{" "}
                    Long sentence (above avg) —{" "}
                    {analysis.longSentences.length} found
                  </span>
                </div>

                <div className="breakdown-text-container">
                  {renderHighlightedText(analysis)}
                </div>

                {/* Complex words list */}
                {analysis.complexWords.length > 0 && (
                  <div className="breakdown-details">
                    <h4>Complex Words ({analysis.complexWords.length})</h4>
                    <div className="word-chips">
                      {analysis.complexWords.map((cw, i) => (
                        <span key={i} className="word-chip highlight-word">
                          {cw.word}{" "}
                          <small>({cw.syllables} syl)</small>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
