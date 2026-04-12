"use client";

import { useEffect, useMemo, useState } from "react";

import { StatusBadge } from "@/components/common/status-badge";
import { useReview } from "@/hooks/useReview";
import { DocumentDetail } from "@/lib/types";
import { documentAssetUrl, documentPageAssetUrl } from "@/lib/api";

export function ReviewEditor({
  document,
  onRefresh,
}: {
  document: DocumentDetail;
  onRefresh: () => Promise<void>;
}) {
  const initialJson = useMemo(
    () => JSON.stringify(document.extraction?.normalized_extraction_json || {}, null, 2),
    [document.extraction],
  );
  const [reviewerName, setReviewerName] = useState("Loan Officer");
  const [comment, setComment] = useState("");
  const [jsonValue, setJsonValue] = useState(initialJson);
  const { submitting, error, saveCorrection, decide } = useReview(document.id, onRefresh);

  useEffect(() => {
    setJsonValue(initialJson);
  }, [initialJson]);

  async function handleSave() {
    const correctedJson = JSON.parse(jsonValue) as Record<string, unknown>;
    await saveCorrection({
      reviewer_name: reviewerName,
      comment,
      corrected_json: correctedJson,
    });
  }

  async function handleDecision(action: "approve" | "reject" | "request_reupload") {
    await decide({
      reviewer_name: reviewerName,
      comment,
      action,
    });
  }

  const primaryPage = document.pages[0];

  return (
    <div className="review-layout">
      <div className="review-column review-column--preview">
        <div className="review-preview-card">
          <div className="review-preview-card__header">
            <div>
              <p className="eyebrow">Document Preview</p>
              <h2>{document.file_name}</h2>
            </div>
            <StatusBadge status={document.status} />
          </div>
          {document.mime_type === "application/pdf" ? (
            <iframe className="preview-frame" src={documentAssetUrl(document.id)} title={document.file_name} />
          ) : primaryPage ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              alt={document.file_name}
              className="preview-image"
              src={documentPageAssetUrl(document.id, primaryPage.page_number, "processed")}
            />
          ) : (
            <div className="preview-placeholder">No page artifact available yet.</div>
          )}
        </div>

        <div className="review-preview-card">
          <p className="eyebrow">Flags</p>
          <ul className="flag-list">
            {document.validation_flags.length === 0 ? <li>No validation flags.</li> : null}
            {document.validation_flags.map((flag) => (
              <li className={`flag flag-${flag.severity}`} key={flag.id}>
                <strong>{flag.flag_code}</strong>
                <span>{flag.message}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="review-preview-card">
          <p className="eyebrow">Review History</p>
          <ul className="history-list">
            {document.review_actions.length === 0 ? <li>No review actions yet.</li> : null}
            {document.review_actions.map((action) => (
              <li key={action.id}>
                <strong>{action.action}</strong> by {action.reviewer_name}
                <span>{action.comment || "No comment"}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="review-preview-card">
          <p className="eyebrow">OCR Raw Text</p>
          <textarea
            readOnly
            rows={12}
            value={document.pages.map((page) => page.ocr_text || "").filter(Boolean).join("\n\n---\n\n")}
          />
        </div>
      </div>

      <div className="review-column">
        <div className="review-preview-card">
          <p className="eyebrow">Extracted Fields</p>
          <div className="form-grid">
            <label>
              Reviewer
              <input value={reviewerName} onChange={(event) => setReviewerName(event.target.value)} />
            </label>
            <label className="form-grid__full">
              Comment
              <textarea rows={3} value={comment} onChange={(event) => setComment(event.target.value)} />
            </label>
            <label className="form-grid__full">
              Corrected JSON
              <textarea rows={18} value={jsonValue} onChange={(event) => setJsonValue(event.target.value)} />
            </label>
          </div>
          <div className="button-row">
            <button className="button button-primary" disabled={submitting} onClick={() => void handleSave()} type="button">
              {submitting ? "Saving..." : "Save Corrections"}
            </button>
            <button className="button button-secondary" disabled={submitting} onClick={() => void handleDecision("approve")} type="button">
              Approve
            </button>
            <button className="button button-secondary" disabled={submitting} onClick={() => void handleDecision("reject")} type="button">
              Reject
            </button>
            <button className="button button-secondary" disabled={submitting} onClick={() => void handleDecision("request_reupload")} type="button">
              Request Re-upload
            </button>
          </div>
          {error ? <p className="feedback feedback-error">{error}</p> : null}
        </div>
      </div>
    </div>
  );
}
