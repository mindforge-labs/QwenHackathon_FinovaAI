"use client";

import { useEffect, useState } from "react";

import { ProgressMeter } from "@/components/common/progress-meter";
import { StatusBadge } from "@/components/common/status-badge";
import {
  buttonStyles,
  emptyState,
  eyebrow,
  feedbackError,
  input,
  inverseEyebrow,
  label,
  sectionCard,
  sectionCardDark,
  signalPillStyles,
  textarea,
} from "@/components/common/ui";
import { useReview } from "@/hooks/useReview";
import { documentAssetUrl, documentPageAssetUrl } from "@/lib/api";
import { DocumentDetail } from "@/lib/types";
import { cn, formatDate, formatDocumentType, formatPercent, formatStatusLabel } from "@/lib/utils";

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

function flagToneClasses(severity: "warning" | "error" | "success") {
  const styles = {
    warning: "border-[#ffd11a]/45 bg-[#ffd11a]/[0.12] text-[#7a5a00]",
    error: "border-[#d03238]/[0.18] bg-[#d03238]/10 text-[#8b1e24]",
    success: "border-[#054d28]/[0.18] bg-[#054d28]/10 text-[#054d28]",
  } as const;

  return cn("flex items-start justify-between gap-4 rounded-[24px] border px-4 py-4", styles[severity]);
}

function timelineToneClasses(tone: DocumentDetail["timeline"][number]["tone"]) {
  const tones = {
    neutral: "bg-black/[0.06]",
    positive: "bg-[#054d28]",
    warning: "bg-[#ffd11a]",
    danger: "bg-[#d03238]",
    pending: "bg-sky-500",
  } as const;

  return tones[tone];
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
    <div className="grid gap-6 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
      <div className="grid gap-6">
        <section className={sectionCardDark}>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className={inverseEyebrow}>Document preview</p>
              <h2 className="mt-2 [font-family:'Arial_Black',Impact,Inter,sans-serif] text-[clamp(2rem,3.8vw,3.2rem)] font-black leading-[0.88] tracking-[-0.05em] text-[#ecf3e2]">
                {document.file_name}
              </h2>
              <p className="mt-3 text-sm leading-6 text-[#ecf3e2]/80">
                {formatDocumentType(document.document_type)} · {document.page_count} page(s)
              </p>
            </div>
            <StatusBadge status={document.status} />
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <span className={signalPillStyles("positive")}>Quality {formatPercent(document.quality_score)}</span>
            <span className={signalPillStyles("inverse")}>OCR {formatPercent(document.ocr_confidence)}</span>
            <span className={signalPillStyles("inverse")}>Extraction {formatPercent(document.extraction_confidence)}</span>
          </div>

          <div className="relative mt-6 overflow-hidden rounded-[30px] border border-white/10 bg-black/20">
            {document.mime_type === "application/pdf" ? (
              <iframe
                className="h-[600px] w-full bg-white"
                src={documentAssetUrl(document.id)}
                title={document.file_name}
              />
            ) : primaryPage ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                alt={document.file_name}
                className="h-auto max-h-[600px] w-full object-contain bg-[#09120a]"
                src={documentPageAssetUrl(document.id, primaryPage.page_number, "processed")}
              />
            ) : (
              <div className="flex min-h-[420px] items-center justify-center px-6 text-center text-sm text-[#ecf3e2]/70">
                No page artifact available yet.
              </div>
            )}

            {document.mime_type !== "application/pdf" && hotspots.length > 0 ? (
              <div className="pointer-events-none absolute inset-0">
                {hotspots.map((hotspot) => (
                  <div
                    className={cn(
                      "absolute overflow-hidden rounded-[18px] border px-2 py-1 text-[0.68rem] font-semibold shadow-[0_8px_18px_rgba(0,0,0,0.18)] backdrop-blur-sm",
                      hotspot.flagged
                        ? "border-[#ffd11a]/60 bg-[#ffd11a]/[0.18] text-[#fff6cb]"
                        : "border-[#9fe870]/50 bg-[#9fe870]/[0.12] text-[#edf9e4]",
                    )}
                    key={hotspot.key}
                    style={hotspot.style}
                  >
                    <span className="block truncate">{getFieldLabel(hotspot.key)}</span>
                    <strong>{Math.round(hotspot.confidence * 100)}%</strong>
                  </div>
                ))}
              </div>
            ) : null}

            <div className="pointer-events-none absolute inset-x-0 top-0 h-10 animate-pulse bg-[linear-gradient(180deg,rgba(255,255,255,0.15),rgba(255,255,255,0))]" />
          </div>
        </section>

        <section className={sectionCard}>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className={eyebrow}>Confidence matrix</p>
              <h2 className="mt-2 [font-family:'Arial_Black',Impact,Inter,sans-serif] text-[clamp(2rem,3.8vw,3.2rem)] font-black leading-[0.88] tracking-[-0.05em] text-[#0e0f0c]">
                AI confidence stack
              </h2>
            </div>
          </div>
          <div className="mt-6 grid gap-4">
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

        <section className={sectionCard}>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className={eyebrow}>Validation</p>
              <h2 className="mt-2 [font-family:'Arial_Black',Impact,Inter,sans-serif] text-[clamp(2rem,3.8vw,3.2rem)] font-black leading-[0.88] tracking-[-0.05em] text-[#0e0f0c]">
                Risk indicators
              </h2>
            </div>
            <span
              className={signalPillStyles(document.validation_flags.length > 0 ? "danger" : "positive")}
            >
              {document.validation_flags.length} active flag{document.validation_flags.length === 1 ? "" : "s"}
            </span>
          </div>
          <ul className="mt-6 grid gap-3">
            {document.validation_flags.length === 0 ? (
              <li className={flagToneClasses("success")}>No validation flags detected.</li>
            ) : null}
            {document.validation_flags.map((flag) => (
              <li className={flagToneClasses(flag.severity === "error" ? "error" : "warning")} key={flag.id}>
                <div>
                  <strong className="block text-sm font-semibold">{flag.flag_code}</strong>
                  <span className="mt-1 block text-sm leading-6">{flag.message}</span>
                </div>
                {flag.field_name ? <em className="text-xs font-semibold uppercase tracking-[0.12em]">{getFieldLabel(flag.field_name)}</em> : null}
              </li>
            ))}
          </ul>
        </section>

        <section className={sectionCard}>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className={eyebrow}>System timeline</p>
              <h2 className="mt-2 [font-family:'Arial_Black',Impact,Inter,sans-serif] text-[clamp(2rem,3.8vw,3.2rem)] font-black leading-[0.88] tracking-[-0.05em] text-[#0e0f0c]">
                What happened to this document
              </h2>
            </div>
          </div>
          <ol className="mt-6 grid gap-4">
            {document.timeline.map((item, index) => (
              <li className="flex gap-4 rounded-[26px] border border-black/10 bg-white/[0.72] px-4 py-4" key={`${item.code}-${item.created_at || index}`}>
                <span className={cn("mt-1.5 h-3 w-3 shrink-0 rounded-full", timelineToneClasses(item.tone))} />
                <div>
                  <strong className="text-sm font-semibold text-[#0e0f0c]">{item.label}</strong>
                  <p className="mt-1 text-sm leading-6 text-[#454745]">{item.description}</p>
                  {item.created_at ? <span className="mt-2 block text-xs font-semibold uppercase tracking-[0.12em] text-[#6c7268]">{formatDate(item.created_at)}</span> : null}
                </div>
              </li>
            ))}
          </ol>
        </section>
      </div>

      <div className="grid gap-6">
        <section className={cn(sectionCard, "border-[#9fe870]/35 bg-[linear-gradient(135deg,rgba(255,255,255,0.92),rgba(245,248,239,0.96))]")}>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className={eyebrow}>Decision controls</p>
              <h2 className="mt-2 [font-family:'Arial_Black',Impact,Inter,sans-serif] text-[clamp(2rem,3.8vw,3.2rem)] font-black leading-[0.88] tracking-[-0.05em] text-[#0e0f0c]">
                Human override lane
              </h2>
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <label className={label}>
              Reviewer
              <input className={input} value={reviewerName} onChange={(event) => setReviewerName(event.target.value)} />
            </label>
            <label className={cn(label, "md:col-span-2")}>
              Comment
              <textarea className={textarea} rows={3} value={comment} onChange={(event) => setComment(event.target.value)} />
            </label>
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            <button
              className={buttonStyles("primary", "justify-center")}
              disabled={submitting || Boolean(jsonError)}
              onClick={() => void handleSave()}
              type="button"
            >
              {submitting ? "Saving..." : "Save corrections"}
            </button>
            <button
              className={buttonStyles("success", "justify-center")}
              disabled={submitting}
              onClick={() => void handleDecision("approve")}
              type="button"
            >
              Approve
            </button>
            <button
              className={buttonStyles("danger", "justify-center")}
              disabled={submitting}
              onClick={() => void handleDecision("reject")}
              type="button"
            >
              Reject
            </button>
            <button
              className={buttonStyles("warning", "justify-center")}
              disabled={submitting}
              onClick={() => void handleDecision("request_reupload")}
              type="button"
            >
              Request re-upload
            </button>
          </div>

          {jsonError ? <p className={cn(feedbackError, "mt-4")}>{jsonError}</p> : null}
          {error ? <p className={cn(feedbackError, "mt-4")}>{error}</p> : null}
        </section>

        <section className={sectionCard}>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className={eyebrow}>Extracted fields</p>
              <h2 className="mt-2 [font-family:'Arial_Black',Impact,Inter,sans-serif] text-[clamp(2rem,3.8vw,3.2rem)] font-black leading-[0.88] tracking-[-0.05em] text-[#0e0f0c]">
                Detected vs reviewed values
              </h2>
            </div>
            <span className={signalPillStyles("soft")}>{orderedEntries.length} field(s)</span>
          </div>

          <div className="mt-6 grid gap-4">
            {orderedEntries.length === 0 ? <p className={emptyState}>No structured extraction is available yet.</p> : null}
            {orderedEntries.map(([key, value]) => {
              const originalValue = originalExtraction[key];
              const signal = fieldSignalMap.get(key);
              const isChanged = JSON.stringify(value) !== JSON.stringify(originalValue);
              const isFlagged = signal?.is_flagged || flaggedFieldNames.has(key);
              const fieldConfidence = signal?.confidence ?? document.extraction_confidence ?? document.ocr_confidence ?? 0.72;
              const readOnly = key === "document_type";

              return (
                <article
                  className={cn(
                    "rounded-[28px] border bg-white/[0.78] p-5 shadow-[0_0_0_1px_rgba(14,15,12,0.04)]",
                    isFlagged ? "border-[#ffd11a]/45" : "border-black/10",
                    isChanged ? "bg-[#9fe870]/[0.08]" : "",
                  )}
                  key={key}
                >
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <p className="text-[0.82rem] font-bold uppercase tracking-[0.12em] text-[#6c7268]">
                        {getFieldLabel(key)}
                      </p>
                      <strong className="mt-2 block text-[1rem] font-semibold text-[#0e0f0c]">
                        {Math.round(fieldConfidence * 100)}% confidence
                      </strong>
                    </div>
                    <div className="flex flex-wrap items-center gap-3">
                      {isFlagged ? <span className={signalPillStyles("danger")}>Flagged</span> : null}
                      {signal?.source === "ocr_line_match" ? (
                        <span className={signalPillStyles("neutral")}>OCR matched</span>
                      ) : null}
                      {signal?.source === "missing" ? <span className={signalPillStyles("danger")}>Missing</span> : null}
                      {isChanged ? <span className={signalPillStyles("positive")}>Edited</span> : null}
                    </div>
                  </div>

                  <label className={cn(label, "mt-5")}>
                    Reviewed value
                    <input
                      className={input}
                      disabled={readOnly}
                      onChange={(event) => updateField(key, event.target.value)}
                      value={formatInputValue(value)}
                    />
                  </label>

                  <div className="mt-5 rounded-[22px] bg-black/[0.03] px-4 py-4">
                    <span className="text-[0.78rem] font-bold uppercase tracking-[0.12em] text-[#6c7268]">AI detected</span>
                    <strong className="mt-2 block text-base font-semibold text-[#0e0f0c]">{formatFieldValue(originalValue)}</strong>
                    {signal?.matched_text ? <span className="mt-2 block text-sm leading-6 text-[#454745]">OCR line: {signal.matched_text}</span> : null}
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        <section className={sectionCard}>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className={eyebrow}>Audit trail</p>
              <h2 className="mt-2 [font-family:'Arial_Black',Impact,Inter,sans-serif] text-[clamp(2rem,3.8vw,3.2rem)] font-black leading-[0.88] tracking-[-0.05em] text-[#0e0f0c]">
                Review history
              </h2>
            </div>
          </div>
          <ul className="mt-6 grid gap-4">
            {document.review_actions.length === 0 ? <li className={emptyState}>No review actions yet.</li> : null}
            {document.review_actions.map((action) => (
              <li className="rounded-[24px] border border-black/10 bg-white/[0.78] px-4 py-4" key={action.id}>
                <div className="flex flex-col gap-2 lg:flex-row lg:items-start lg:justify-between">
                  <strong className="text-sm font-semibold text-[#0e0f0c]">{formatStatusLabel(action.action)}</strong>
                  <span className="text-xs font-semibold uppercase tracking-[0.12em] text-[#6c7268]">{formatDate(action.created_at)}</span>
                </div>
                <p className="mt-3 text-sm font-semibold text-[#0e0f0c]">{action.reviewer_name}</p>
                <span className="mt-2 block text-sm leading-6 text-[#454745]">{action.comment || "No comment provided."}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className={sectionCard}>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className={eyebrow}>JSON payload</p>
              <h2 className="mt-2 [font-family:'Arial_Black',Impact,Inter,sans-serif] text-[clamp(2rem,3.8vw,3.2rem)] font-black leading-[0.88] tracking-[-0.05em] text-[#0e0f0c]">
                Structured extraction payload
              </h2>
            </div>
          </div>
          <textarea className={cn(textarea, "mt-6 font-mono text-xs")} rows={14} value={jsonValue} onChange={(event) => handleJsonChange(event.target.value)} />
        </section>

        <section className={sectionCard}>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className={eyebrow}>OCR raw text</p>
              <h2 className="mt-2 [font-family:'Arial_Black',Impact,Inter,sans-serif] text-[clamp(2rem,3.8vw,3.2rem)] font-black leading-[0.88] tracking-[-0.05em] text-[#0e0f0c]">
                Source text evidence
              </h2>
            </div>
          </div>
          <textarea
            className={cn(textarea, "mt-6 font-mono text-xs")}
            readOnly
            rows={12}
            value={document.pages.map((page) => page.ocr_text || "").filter(Boolean).join("\n\n---\n\n")}
          />
        </section>
      </div>
    </div>
  );
}
