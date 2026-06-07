/**
 * DatabaseViewer — Admin page to visualize documents and versions.
 * Shows real-time data from PostgreSQL for demo verification.
 */

import { useCallback, useEffect, useState } from "react";
import type { DocumentOut, VersionOut } from "../types/rewrite";
import "./DatabaseViewer.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

interface DocumentWithVersions extends DocumentOut {
  versions: VersionOut[];
  expanded: boolean;
}

export default function DatabaseViewer() {
  const [documents, setDocuments] = useState<DocumentWithVersions[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/documents`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const docs: DocumentOut[] = await res.json();

      const docsWithVersions: DocumentWithVersions[] = await Promise.all(
        docs.map(async (doc) => {
          const vRes = await fetch(`${API_BASE}/documents/${doc.id}/versions`);
          const versions: VersionOut[] = vRes.ok ? await vRes.json() : [];
          return { ...doc, versions, expanded: true };
        })
      );

      setDocuments(docsWithVersions);
      setLastRefresh(new Date());
    } catch (err: any) {
      setError(err.message || "Failed to fetch data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const toggleExpand = (docId: string) => {
    setDocuments((prev) =>
      prev.map((d) =>
        d.id === docId ? { ...d, expanded: !d.expanded } : d
      )
    );
  };

  const formatDate = (iso: string) => {
    return new Date(iso).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  const truncate = (text: string, max: number) =>
    text.length > max ? text.slice(0, max) + "…" : text;

  return (
    <div className="db-viewer">
      <header className="db-header">
        <div className="db-header-left">
          <h1>
            <span className="db-icon">🗄️</span> Database Viewer
          </h1>
          <span className="db-subtitle">PostgreSQL — accessibility_rewriter</span>
        </div>
        <div className="db-header-right">
          <span className="db-refresh-time">
            Last refresh: {lastRefresh.toLocaleTimeString()}
          </span>
          <button className="btn-refresh" onClick={fetchData} disabled={loading}>
            {loading ? "⟳ Loading…" : "⟳ Refresh"}
          </button>
        </div>
      </header>

      {error && (
        <div className="db-error">
          ⚠️ {error}
        </div>
      )}

      {/* ── Stats Bar ──────────────────────────────────────────── */}
      <div className="db-stats">
        <div className="stat-card">
          <span className="stat-value">{documents.length}</span>
          <span className="stat-label">Documents</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">
            {documents.reduce((sum, d) => sum + d.versions.length, 0)}
          </span>
          <span className="stat-label">Total Versions</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">2</span>
          <span className="stat-label">Tables</span>
        </div>
      </div>

      {/* ── Documents Table ────────────────────────────────────── */}
      <section className="db-section">
        <h2 className="section-title">
          <span className="table-icon">📄</span> documents
          <span className="row-count">{documents.length} rows</span>
        </h2>

        {documents.length === 0 && !loading && (
          <div className="db-empty">No documents found.</div>
        )}

        {documents.map((doc) => (
          <div key={doc.id} className="doc-card">
            <div className="doc-row" onClick={() => toggleExpand(doc.id)}>
              <span className={`expand-arrow ${doc.expanded ? "expanded" : ""}`}>
                ▶
              </span>
              <div className="doc-fields">
                <div className="field">
                  <span className="field-label">id</span>
                  <span className="field-value mono">{doc.id}</span>
                </div>
                <div className="field">
                  <span className="field-label">title</span>
                  <span className="field-value">{doc.title}</span>
                </div>
                <div className="field">
                  <span className="field-label">content</span>
                  <span className="field-value dimmed">
                    {truncate(doc.content, 80)}
                  </span>
                </div>
                <div className="field">
                  <span className="field-label">created_at</span>
                  <span className="field-value">{formatDate(doc.created_at)}</span>
                </div>
              </div>
              <div className="version-badge">
                {doc.versions.length} version{doc.versions.length !== 1 ? "s" : ""}
              </div>
            </div>

            {/* ── Versions sub-table ──────────────────────────── */}
            {doc.expanded && doc.versions.length > 0 && (
              <div className="versions-panel">
                <h3 className="versions-title">
                  <span className="table-icon">📋</span> document_versions
                  <span className="row-count">
                    {doc.versions.length} rows (document_id = {doc.id.slice(0, 8)}…)
                  </span>
                </h3>
                <div className="versions-table-wrapper">
                  <table className="versions-table">
                    <thead>
                      <tr>
                        <th>version_number</th>
                        <th>reading_level</th>
                        <th>author</th>
                        <th>content</th>
                        <th>created_at</th>
                      </tr>
                    </thead>
                    <tbody>
                      {doc.versions.map((v) => (
                        <tr key={v.id}>
                          <td className="center">
                            <span className="version-num">v{v.version_number}</span>
                          </td>
                          <td>
                            <span className="level-pill">{v.reading_level}</span>
                          </td>
                          <td>{v.author}</td>
                          <td className="content-cell">
                            {truncate(v.content, 120)}
                          </td>
                          <td className="mono">{formatDate(v.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {doc.expanded && doc.versions.length === 0 && (
              <div className="versions-panel">
                <div className="db-empty">No versions saved yet for this document.</div>
              </div>
            )}
          </div>
        ))}
      </section>

      {/* ── Navigation ─────────────────────────────────────────── */}
      <footer className="db-footer">
        <a href="/" className="back-link">← Back to Rewrite Page</a>
      </footer>
    </div>
  );
}
