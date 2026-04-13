"use client";

import { useEffect, useState } from "react";

import { ProgressMeter } from "@/components/common/progress-meter";
import { StatusBadge } from "@/components/common/status-badge";
import { useReview } from "@/hooks/useReview";
import { documentAssetUrl, documentPageAssetUrl } from "@/lib/api";
import { DocumentDetail } from "@/lib/types";
import { formatDate, formatDocumentType, formatPercent, formatStatusLabel } from "@/lib/utils";

const FIELD_LABELS: Record<string, string> = {
  document_type: "Document type",
  full_name: "Full name",
  dob: "Date of birth",
  id_number: "ID number",
  address: "Address",
  issue_date: "Issue date",
  employee_name: "Employee name",
  employer_name: "Employer name",
  pay_period: "Pay period",
  gross_salary: "Gross salary",
  net_salary: "Net salary",
  account_holder: "Account holder",
  bank_name: "Bank name",
  account_number: "Account number",
  statement_period: "Statement period",
  ending_balance: "Ending balance",
};

const FIELD_ORDER: Record<string, string[]> = {
  id_card: ["document_type", "full_name", "id_number", "dob", "address", "issue_date"],
  payslip: ["document_type", "employee_name", "employer_name", "pay_period", "gross_salary", "net_salary"],
  bank_statement: [
    "document_type",
    "account_holder",
    "bank_name",
    "account_number",
    "statement_period",
    "ending_balance",
  ],
};

function getOrderedEntries(documentType: string | null, payload: Record<string, unknown>) {
  const order = FIELD_ORDER[documentType || ""] || [];

  return Object.entries(payload).sort(([leftKey], [rightKey]) => {
    const leftIndex = order.indexOf(leftKey);
    const rightIndex = order.indexOf(rightKey);

    if (leftIndex === -1 && rightIndex === -1) {
      return leftKey.localeCompare(rightKey);
    }

    if (leftIndex === -1) {
      return 1;
    }

    if (rightIndex === -1) {
      return -1;
    }

    return leftIndex - rightIndex;
  });
}

function formatFieldValue(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "Missing";
  }

  if (typeof value === "number") {
    return new Intl.NumberFormat("en-US", {
      maximumFractionDigits: 2,
    }).format(value);
  }

  if (typeof value === "string") {
    return value;
  }

  return JSON.stringify(value);
}

function formatInputValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "";
  }

  if (typeof value === "string") {
    return value;
  }

  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }

  return JSON.stringify(value);
}

function parseInputValue(rawValue: string, originalValue: unknown): unknown {
  if (rawValue.trim() === "") {
    return null;
  }

  if (typeof originalValue === "number") {
    const normalized = Number(rawValue.replace(/,/g, ""));
    return Number.isFinite(normalized) ? normalized : rawValue;
  }

  if (typeof originalValue === "boolean") {
    return rawValue.toLowerCase() === "true";
  }

  if (typeof originalValue === "object" && originalValue !== null) {
    try {
      return JSON.parse(rawValue);
    } catch {
      return rawValue;
    }
  }

  return rawValue;
}

function getFieldLabel(key: string): string {
  return FIELD_LABELS[key] || key.replace(/_/g, " ");
}

function toPreviewStyle(
  bbox: number[][] | null,
  extent: { width: number; height: number } | null,
): { top: string; left: string; width: string; height: string } | null {
  if (!bbox || bbox.length === 0 || !extent || extent.width <= 0 || extent.height <= 0) {
    return null;
  }

  const xs = bbox.map((point) => point[0]);
  const ys = bbox.map((point) => point[1]);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);

  return {
    top: `${(minY / extent.height) * 100}%`,
    left: `${(minX / extent.width) * 100}%`,
    width: `${((maxX - minX) / extent.width) * 100}%`,
    height: `${((maxY - minY) / extent.height) * 100}%`,
  };
}

export function ReviewEditor({
  document,
  onRefresh,
}: {
  document: DocumentDetail;
  onRefresh: () => Promise<void>;
}) {
  const originalExtraction = document.extraction?.normalized_extraction_json || {};
  const [reviewerName, setReviewerName] = useState("Loan Officer");
  const [comment, setComment] = useState("");
  const [draftFields, setDraftFields] = useState<Record<string, unknown>>(originalExtraction);
  const [jsonValue, setJsonValue] = useState(JSON.stringify(originalExtraction, null, 2));
  const [jsonError, setJsonError] = useState<string | null>(null);
  const { submitting, error, saveCorrection, decide } = useReview(document.id, onRefresh);

  useEffect(() => {
    const nextValue = document.extraction?.normalized_extraction_json || {};
    setDraftFields(nextValue);
    setJsonValue(JSON.stringify(nextValue, null, 2));
    setJsonError(null);
  }, [document.id, document.extraction?.updated_at]);

  const orderedEntries = getOrderedEntries(document.document_type, draftFields);
  const fieldSignalMap = new Map(document.field_signals.map((signal) => [signal.field_name, signal]));
  const flaggedFieldNames = new Set(
    document.validation_flags
      .map((flag) => flag.field_name)
      .filter((value): value is string => Boolean(value)),
  );
  const primaryPage = document.pages[0];
  const previewExtent = primaryPage
    ? primaryPage.ocr_lines.reduce(
        (extent, line) => ({
          width: Math.max(extent.width, ...line.bbox.map((point) => point[0])),
          height: Math.max(extent.height, ...line.bbox.map((point) => point[1])),
        }),
        { width: 0, height: 0 },
      )
    : null;
  const hotspots = document.field_signals
    .filter((signal) => signal.page_number === primaryPage?.page_number && signal.bbox)
    .slice(0, 5)
    .map((signal) => ({
      key: signal.field_name,
      confidence: signal.confidence ?? document.extraction_confidence ?? 0,
      flagged: signal.is_flagged,
      style: toPreviewStyle(signal.bbox, previewExtent),
    }))
    .filter(
      (
        signal,
      ): signal is {
        key: string;
        confidence: number;
        flagged: boolean;
        style: { top: string; left: string; width: string; height: string };
      } => Boolean(signal.style),
    );

  function updateField(key: string, rawValue: string) {
    const nextFields = {
      ...draftFields,
      [key]: parseInputValue(rawValue, originalExtraction[key]),
    };
    setDraftFields(nextFields);
    setJsonValue(JSON.stringify(nextFields, null, 2));
    setJsonError(null);
  }

  function handleJsonChange(value: string) {
    setJsonValue(value);

    try {
      const parsed = JSON.parse(value) as Record<string, unknown>;
      setDraftFields(parsed);
      setJsonError(null);
    } catch {
      setJsonError("JSON must stay valid before saving corrections.");
    }
  }

  async function handleSave() {
    if (jsonError) {
      return;
    }

    await saveCorrection({
      reviewer_name: reviewerName,
      comment,
      corrected_json: draftFields,
    });
  }

  async function handleDecision(action: "approve" | "reject" | "request_reupload") {
    await decide({
      reviewer_name: reviewerName,
      comment,
      action,
    });
  }

  return (
    <div className="review-layout">
      <div className="review-column review-column--preview">
        <section className="review-preview-card review-preview-card--dark">
          <div className="review-preview-card__header">
            <div>
              <p className="eyebrow eyebrow--inverse">Document preview</p>
              <h2>{document.file_name}</h2>
              <p>{formatDocumentType(document.document_type)} · {document.page_count} page(s)</p>
            </div>
            <StatusBadge status={document.status} />
          </div>

          <div className="review-preview-card__meta">
            <span className="signal-pill signal-pill--positive">Quality {formatPercent(document.quality_score)}</span>
            <span className="signal-pill signal-pill--soft">OCR {formatPercent(document.ocr_confidence)}</span>
            <span className="signal-pill signal-pill--soft">Extraction {formatPercent(document.extraction_confidence)}</span>
          </div>

          <div className="review-preview-stage">
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

            {document.mime_type !== "application/pdf" && hotspots.length > 0 ? (
              <div className="preview-hotspots">
                {hotspots.map((hotspot) => (
                  <div
                    className={`preview-hotspot ${hotspot.flagged ? "preview-hotspot--warning" : "preview-hotspot--default"}`}
                    key={hotspot.key}
                    style={hotspot.style}
                  >
                    <span>{getFieldLabel(hotspot.key)}</span>
                    <strong>{Math.round(hotspot.confidence * 100)}%</strong>
                  </div>
                ))}
              </div>
            ) : null}

            <div className="preview-scanline" />
          </div>
        </section>

        <section className="review-preview-card">
          <div className="review-preview-card__header">
            <div>
              <p className="eyebrow">Confidence matrix</p>
              <h2>AI confidence stack</h2>
            </div>
          </div>
          <div className="meter-stack">
            <ProgressMeter
              label="Image quality"
              tone={document.quality_score !== null && document.quality_score >= 0.75 ? "positive" : "warning"}
              value={(document.quality_score || 0) * 100}
            />
            <ProgressMeter
              label="OCR confidence"
              tone={document.ocr_confidence !== null && document.ocr_confidence >= 0.75 ? "positive" : "warning"}
              value={(document.ocr_confidence || 0) * 100}
            />
            <ProgressMeter
              label="Extraction confidence"
              tone={
                document.extraction_confidence !== null && document.extraction_confidence >= 0.75
                  ? "positive"
                  : "warning"
              }
              value={(document.extraction_confidence || 0) * 100}
            />
          </div>
        </section>

        <section className="review-preview-card">
          <div className="review-preview-card__header">
            <div>
              <p className="eyebrow">Validation</p>
              <h2>Risk indicators</h2>
            </div>
            <span
              className={`signal-pill ${document.validation_flags.length > 0 ? "signal-pill--danger" : "signal-pill--positive"}`}
            >
              {document.validation_flags.length} active flag{document.validation_flags.length === 1 ? "" : "s"}
            </span>
          </div>
          <ul className="flag-list">
            {document.validation_flags.length === 0 ? (
              <li className="flag flag-success">No validation flags detected.</li>
            ) : null}
            {document.validation_flags.map((flag) => (
              <li className={`flag flag-${flag.severity}`} key={flag.id}>
                <div>
                  <strong>{flag.flag_code}</strong>
                  <span>{flag.message}</span>
                </div>
                {flag.field_name ? <em>{getFieldLabel(flag.field_name)}</em> : null}
              </li>
            ))}
          </ul>
        </section>

        <section className="review-preview-card">
          <div className="review-preview-card__header">
            <div>
              <p className="eyebrow">System timeline</p>
              <h2>What happened to this document</h2>
            </div>
          </div>
          <ol className="timeline-list">
            {document.timeline.map((item, index) => (
              <li className={`timeline-item timeline-item--${item.tone}`} key={`${item.code}-${item.created_at || index}`}>
                <span className="timeline-item__dot" />
                <div>
                  <strong>{item.label}</strong>
                  <p>{item.description}</p>
                  {item.created_at ? <span>{formatDate(item.created_at)}</span> : null}
                </div>
              </li>
            ))}
          </ol>
        </section>
      </div>

      <div className="review-column">
        <section className="review-preview-card review-preview-card--accent">
          <div className="review-preview-card__header">
            <div>
              <p className="eyebrow">Decision controls</p>
              <h2>Human override lane</h2>
            </div>
          </div>

          <div className="form-grid">
            <label>
              Reviewer
              <input value={reviewerName} onChange={(event) => setReviewerName(event.target.value)} />
            </label>
            <label className="form-grid__full">
              Comment
              <textarea rows={3} value={comment} onChange={(event) => setComment(event.target.value)} />
            </label>
          </div>

          <div className="decision-grid">
            <button
              className="button button-primary"
              disabled={submitting || Boolean(jsonError)}
              onClick={() => void handleSave()}
              type="button"
            >
              {submitting ? "Saving..." : "Save corrections"}
            </button>
            <button
              className="button button-success"
              disabled={submitting}
              onClick={() => void handleDecision("approve")}
              type="button"
            >
              Approve
            </button>
            <button
              className="button button-danger"
              disabled={submitting}
              onClick={() => void handleDecision("reject")}
              type="button"
            >
              Reject
            </button>
            <button
              className="button button-warning"
              disabled={submitting}
              onClick={() => void handleDecision("request_reupload")}
              type="button"
            >
              Request re-upload
            </button>
          </div>

          {jsonError ? <p className="feedback feedback-error">{jsonError}</p> : null}
          {error ? <p className="feedback feedback-error">{error}</p> : null}
        </section>

        <section className="review-preview-card">
          <div className="review-preview-card__header">
            <div>
              <p className="eyebrow">Extracted fields</p>
              <h2>Detected vs reviewed values</h2>
            </div>
            <span className="signal-pill signal-pill--soft">{orderedEntries.length} field(s)</span>
          </div>

          <div className="field-card-grid">
            {orderedEntries.length === 0 ? <p className="empty-state">No structured extraction is available yet.</p> : null}
            {orderedEntries.map(([key, value]) => {
              const originalValue = originalExtraction[key];
              const signal = fieldSignalMap.get(key);
              const isChanged = JSON.stringify(value) !== JSON.stringify(originalValue);
              const isFlagged = signal?.is_flagged || flaggedFieldNames.has(key);
              const fieldConfidence = signal?.confidence ?? document.extraction_confidence ?? document.ocr_confidence ?? 0.72;
              const readOnly = key === "document_type";

              return (
                <article
                  className={[
                    "field-card",
                    isFlagged ? "field-card--flagged" : "",
                    isChanged ? "field-card--changed" : "",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                  key={key}
                >
                  <div className="field-card__header">
                    <div>
                      <p>{getFieldLabel(key)}</p>
                      <strong>{Math.round(fieldConfidence * 100)}% confidence</strong>
                    </div>
                    <div className="field-card__signals">
                      {isFlagged ? <span className="signal-pill signal-pill--danger">Flagged</span> : null}
                      {signal?.source === "ocr_line_match" ? (
                        <span className="signal-pill signal-pill--neutral">OCR matched</span>
                      ) : null}
                      {signal?.source === "missing" ? <span className="signal-pill signal-pill--danger">Missing</span> : null}
                      {isChanged ? <span className="signal-pill signal-pill--positive">Edited</span> : null}
                    </div>
                  </div>

                  <label>
                    Reviewed value
                    <input
                      disabled={readOnly}
                      onChange={(event) => updateField(key, event.target.value)}
                      value={formatInputValue(value)}
                    />
                  </label>

                  <div className="field-card__compare">
                    <span>AI detected</span>
                    <strong>{formatFieldValue(originalValue)}</strong>
                    {signal?.matched_text ? <span>OCR line: {signal.matched_text}</span> : null}
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        <section className="review-preview-card">
          <div className="review-preview-card__header">
            <div>
              <p className="eyebrow">Audit trail</p>
              <h2>Review history</h2>
            </div>
          </div>
          <ul className="history-list">
            {document.review_actions.length === 0 ? <li className="history-item">No review actions yet.</li> : null}
            {document.review_actions.map((action) => (
              <li className="history-item" key={action.id}>
                <div className="history-item__header">
                  <strong>{formatStatusLabel(action.action)}</strong>
                  <span>{formatDate(action.created_at)}</span>
                </div>
                <p>{action.reviewer_name}</p>
                <span>{action.comment || "No comment provided."}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="review-preview-card">
          <div className="review-preview-card__header">
            <div>
              <p className="eyebrow">JSON payload</p>
              <h2>Structured extraction payload</h2>
            </div>
          </div>
          <textarea rows={14} value={jsonValue} onChange={(event) => handleJsonChange(event.target.value)} />
        </section>

        <section className="review-preview-card">
          <div className="review-preview-card__header">
            <div>
              <p className="eyebrow">OCR raw text</p>
              <h2>Source text evidence</h2>
            </div>
          </div>
          <textarea
            readOnly
            rows={12}
            value={document.pages.map((page) => page.ocr_text || "").filter(Boolean).join("\n\n---\n\n")}
          />
        </section>
      </div>
    </div>
  );
}
