/**
 * AltTextPage — UC3: GenerateImageAltText
 *
 * Dedicated page for uploading images, generating WCAG-compliant alt text
 * via AI vision, reviewing/editing, and approving.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import "./AltTextPage.css";

const API_BASE = "http://localhost:8000/api";

// Default document ID (same as seeded document)
const DEFAULT_DOC_ID = "11111111-1111-1111-1111-111111111111";

interface ImageRecord {
  id: string;
  document_id: string;
  filename: string;
  image_url: string;
  alt_text: string | null;
  alt_text_status: string;
  purpose_note: string | null;
}

type PageState =
  | "idle"
  | "image-ready"
  | "generating"
  | "review"
  | "too-complex"
  | "error";

export default function AltTextPage() {
  // ── State ───────────────────────────────────────────────────────
  const [images, setImages] = useState<ImageRecord[]>([]);
  const [selectedImage, setSelectedImage] = useState<ImageRecord | null>(null);
  const [purposeNote, setPurposeNote] = useState("");
  const [generatedAltText, setGeneratedAltText] = useState("");
  const [editedAltText, setEditedAltText] = useState("");
  const [pageState, setPageState] = useState<PageState>("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [selectPrompt, setSelectPrompt] = useState("");
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // ── Fetch images ────────────────────────────────────────────────
  const fetchImages = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/images`);
      if (res.ok) {
        const data = await res.json();
        setImages(data);
      }
    } catch {
      // silent
    }
  }, []);

  useEffect(() => {
    fetchImages();
  }, [fetchImages]);

  // ── Upload ──────────────────────────────────────────────────────
  const handleFileSelect = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("document_id", DEFAULT_DOC_ID);

    try {
      const res = await fetch(`${API_BASE}/images/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        setErrorMessage(err.detail || "Upload failed");
        setPageState("error");
        return;
      }

      const img: ImageRecord = await res.json();
      setImages((prev) => [...prev, img]);
      setSelectedImage(img);
      setPreviewUrl(URL.createObjectURL(file));
      setPageState("image-ready");
      setSelectPrompt("");
      setErrorMessage("");
    } catch {
      setErrorMessage("Failed to upload image");
      setPageState("error");
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) {
      handleFileSelect(file);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFileSelect(file);
  };

  // ── Select from gallery ─────────────────────────────────────────
  const handleSelectFromGallery = (img: ImageRecord) => {
    setSelectedImage(img);
    // Build preview URL from uploaded file
    setPreviewUrl(`http://localhost:8000${img.image_url}`);
    setPageState("image-ready");
    setGeneratedAltText("");
    setEditedAltText("");
    setPurposeNote("");
    setSelectPrompt("");
    setErrorMessage("");
    setSuccessMessage("");
  };

  // ── Generate ────────────────────────────────────────────────────
  const handleGenerate = async () => {
    if (!selectedImage) {
      setSelectPrompt("Please select an image first");
      return;
    }

    setPageState("generating");
    setErrorMessage("");
    setSelectPrompt("");

    try {
      const res = await fetch(
        `${API_BASE}/images/${selectedImage.id}/generate`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            purpose_note: purposeNote.trim() || null,
          }),
        }
      );

      if (res.status === 503) {
        setErrorMessage("AI vision service is unavailable. Please try again.");
        setPageState("error");
        return;
      }

      if (!res.ok) {
        const err = await res.json();
        setErrorMessage(err.detail || "Generation failed");
        setPageState("error");
        return;
      }

      const data = await res.json();

      if (data.is_too_complex) {
        setPageState("too-complex");
        setEditedAltText("");
      } else {
        setGeneratedAltText(data.alt_text);
        setEditedAltText(data.alt_text);
        setPageState("review");
      }
    } catch {
      setErrorMessage("Failed to connect to the server");
      setPageState("error");
    }
  };

  // ── Approve ─────────────────────────────────────────────────────
  const handleApprove = async () => {
    if (!selectedImage) return;

    const textToSave = editedAltText.trim();
    if (!textToSave) return;

    try {
      const res = await fetch(
        `${API_BASE}/images/${selectedImage.id}/approve`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ alt_text: textToSave }),
        }
      );

      if (res.ok) {
        const updated: ImageRecord = await res.json();
        setImages((prev) =>
          prev.map((img) => (img.id === updated.id ? updated : img))
        );
        setSelectedImage(updated);
        setPageState("idle");
        setGeneratedAltText("");
        setEditedAltText("");
        setPurposeNote("");
        setSuccessMessage("Alt text saved successfully");
        setTimeout(() => setSuccessMessage(""), 3000);
      }
    } catch {
      setErrorMessage("Failed to save alt text");
      setPageState("error");
    }
  };

  // ── Regenerate ──────────────────────────────────────────────────
  const handleRegenerate = async () => {
    await handleGenerate();
  };

  // ── Cancel ──────────────────────────────────────────────────────
  const handleCancel = async () => {
    if (selectedImage) {
      try {
        await fetch(`${API_BASE}/images/${selectedImage.id}/cancel`, {
          method: "PUT",
        });
        await fetchImages();
      } catch {
        // silent
      }
    }
    setPageState("image-ready");
    setGeneratedAltText("");
    setEditedAltText("");
  };

  // ── Remove selected image ───────────────────────────────────────
  const handleRemoveImage = () => {
    setSelectedImage(null);
    setPreviewUrl(null);
    setPageState("idle");
    setGeneratedAltText("");
    setEditedAltText("");
    setPurposeNote("");
  };

  // ── Derived state ───────────────────────────────────────────────
  const allDescribed =
    images.length > 0 && images.every((img) => img.alt_text_status === "described");
  const noImages = images.length === 0;
  const charCount = editedAltText.length;

  // ── Render ──────────────────────────────────────────────────────
  return (
    <div id="alttext-page" className="alttext-page">
      <header className="alttext-header">
        <h1>Generate Image Alt Text</h1>
      </header>

      {/* ── Error Banner ─────────────────────────────────────── */}
      {pageState === "error" && (
        <div id="error-banner" className="error-banner">
          <span>{errorMessage}</span>
          <button
            id="retry-btn"
            className="btn btn-secondary"
            onClick={handleGenerate}
          >
            🔄 Retry
          </button>
        </div>
      )}

      {/* ── Select Prompt ────────────────────────────────────── */}
      {selectPrompt && (
        <div id="select-prompt" className="select-prompt">
          {selectPrompt}
        </div>
      )}

      {/* ── Upload Area ──────────────────────────────────────── */}
      <section className="upload-section">
        <div
          className={`upload-drop-zone ${selectedImage ? "has-image" : ""}`}
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => !selectedImage && fileInputRef.current?.click()}
        >
          {selectedImage && previewUrl ? (
            <div className="image-preview-container">
              <img
                id="image-preview"
                src={previewUrl}
                alt="Preview"
                className="image-preview-thumb"
              />
              <div className="image-preview-info">
                <div className="image-preview-name">
                  {selectedImage.filename}
                </div>
                <div className="image-preview-meta">
                  Status: {selectedImage.alt_text_status}
                </div>
              </div>
              <button
                className="remove-image-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  handleRemoveImage();
                }}
                title="Remove"
              >
                ✕
              </button>
            </div>
          ) : (
            <>
              <div className="upload-icon">🖼️</div>
              <div className="upload-text">
                Drop an image here or click to browse
              </div>
              <div className="upload-hint">
                Supports JPEG, PNG, GIF, WebP
              </div>
            </>
          )}
        </div>
        <input
          id="image-upload"
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/gif,image/webp"
          className="upload-input"
          onChange={handleInputChange}
        />
      </section>

      {/* ── Purpose Note ─────────────────────────────────────── */}
      {selectedImage && pageState !== "review" && pageState !== "too-complex" && (
        <section className="note-section">
          <label className="label" htmlFor="purpose-note">
            Purpose Note (optional)
          </label>
          <textarea
            id="purpose-note"
            className="purpose-textarea"
            rows={2}
            value={purposeNote}
            onChange={(e) => setPurposeNote(e.target.value)}
            placeholder="Describe the image's purpose (e.g., 'Diagram showing the water cycle')…"
          />
        </section>
      )}

      {/* ── Generate Button ──────────────────────────────────── */}
      {(pageState === "image-ready" || pageState === "idle") && (
        <div className="controls-row">
          <button
            id="generate-btn"
            className="btn btn-generate"
            onClick={handleGenerate}
          >
            🖼️ Generate Alt Text
          </button>
        </div>
      )}

      {/* ── Generating Spinner ───────────────────────────────── */}
      {pageState === "generating" && (
        <div className="generating-spinner">
          <span className="spinner-dot" />
          Generating alt text…
        </div>
      )}

      {/* ── Review Panel ─────────────────────────────────────── */}
      {pageState === "review" && (
        <div id="alttext-review" className="review-panel">
          <h3>📝 Review Generated Alt Text</h3>
          <textarea
            id="alttext-textarea"
            className="alttext-input"
            rows={3}
            value={editedAltText}
            onChange={(e) => setEditedAltText(e.target.value)}
          />
          <span
            id="char-counter"
            className={`char-counter ${charCount > 125 ? "over-limit" : ""}`}
          >
            {charCount} / 125 characters
          </span>
          <div className="review-actions">
            <button
              id="approve-btn"
              className="btn btn-approve"
              onClick={handleApprove}
              disabled={!editedAltText.trim()}
            >
              ✅ Approve
            </button>
            <button
              id="regenerate-btn"
              className="btn btn-secondary"
              onClick={handleRegenerate}
            >
              🔄 Regenerate
            </button>
            <button
              id="cancel-btn"
              className="btn btn-secondary"
              onClick={handleCancel}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* ── Too Complex Panel ────────────────────────────────── */}
      {pageState === "too-complex" && (
        <div id="manual-input-panel" className="manual-panel">
          <div id="complex-warning" className="complex-warning-banner">
            ⚠️ This image is too complex for automatic description. Please
            write alt text manually.
          </div>
          <label className="label" htmlFor="manual-alttext">
            Manual Alt Text
          </label>
          <textarea
            id="manual-alttext"
            className="alttext-input"
            rows={3}
            value={editedAltText}
            onChange={(e) => setEditedAltText(e.target.value)}
            placeholder="Describe the image manually…"
          />
          <span
            className={`char-counter ${charCount > 125 ? "over-limit" : ""}`}
          >
            {charCount} / 125 characters
          </span>
          <div className="review-actions">
            <button
              id="approve-btn"
              className="btn btn-approve"
              onClick={handleApprove}
              disabled={!editedAltText.trim()}
            >
              ✅ Approve
            </button>
            <button
              id="cancel-btn"
              className="btn btn-secondary"
              onClick={handleCancel}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* ── Success Toast ────────────────────────────────────── */}
      {successMessage && (
        <div id="success-toast" className="success-toast">
          {successMessage}
        </div>
      )}

      {/* ── Image Gallery ────────────────────────────────────── */}
      <section className="gallery-section">
        <h2>Image Gallery</h2>

        {noImages && (
          <div id="no-images-msg" className="info-banner">
            No images found in this document
          </div>
        )}

        {allDescribed && !noImages && (
          <div id="all-described-msg" className="info-banner" style={{ color: "#3fb950" }}>
            ✅ All images are described
          </div>
        )}

        <div id="image-gallery" className="image-gallery">
          {images.map((img) => (
            <div
              key={img.id}
              className={`image-card ${selectedImage?.id === img.id ? "selected" : ""}`}
              onClick={() => handleSelectFromGallery(img)}
            >
              <img
                src={`http://localhost:8000${img.image_url}`}
                alt={img.alt_text || img.filename}
                className="image-card-thumb"
              />
              <div className="image-card-footer">
                <span className="image-card-name">{img.filename}</span>
                <span
                  id={`${img.alt_text_status}-badge`}
                  className={`status-badge ${img.alt_text_status}`}
                >
                  {img.alt_text_status === "described" ? "✅ Described" : "⚠️ Missing"}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
