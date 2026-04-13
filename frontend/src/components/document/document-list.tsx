"use client";

import Link from "next/link";

import { ProgressMeter } from "@/components/common/progress-meter";
import { StatusBadge } from "@/components/common/status-badge";
import { DocumentStatus, DocumentSummary } from "@/lib/types";
import { formatDate, formatDocumentType, formatStatusLabel } from "@/lib/utils";

const STATUS_PROGRESS: Record<DocumentStatus, number> = {
  uploaded: 12,
  processing: 48,
  processed: 78,
  needs_review: 88,
  approved: 100,
  rejected: 100,
  failed: 100,
};

export function DocumentList({
  documents,
  onProcess,
}: {
  documents: DocumentSummary[];
  onProcess: (documentId: string) => Promise<void>;
}) {
  const groups = [
    {
      key: "review",
      title: "Review queue",
      subtitle: "Warnings, low-confidence cases, and rejected outputs that need human attention.",
      items: documents.filter(
        (document) =>
          document.status === "needs_review" ||
          document.status === "failed" ||
          document.status === "rejected" ||
          document.validation_flag_count > 0,
      ),
    },
    {
      key: "pipeline",
      title: "Pipeline activity",
      subtitle: "Files still moving through upload, OCR, and extraction.",
      items: documents.filter(
        (document) =>
          document.status === "uploaded" ||
          document.status === "processing",
      ),
    },
    {
      key: "cleared",
      title: "Ready and resolved",
      subtitle: "Documents that completed extraction and are ready or already cleared.",
      items: documents.filter(
        (document) =>
          document.status === "processed" || document.status === "approved",
      ),
    },
  ].filter((group) => group.items.length > 0);

  if (documents.length === 0) {
    return <p className="empty-state">No documents uploaded yet.</p>;
  }

  return (
    <div className="document-groups">
      {groups.map((group) => (
        <section className="document-group" key={group.key}>
          <header className="document-group__header">
            <div>
              <p className="eyebrow">{group.title}</p>
              <h3>{group.items.length} document(s)</h3>
            </div>
            <p>{group.subtitle}</p>
          </header>

          <div className="document-list">
            {group.items.map((document) => {
              const needsAttention =
                document.validation_flag_count > 0 ||
                document.status === "needs_review" ||
                document.status === "failed" ||
                document.status === "rejected";
              const processDisabled = document.status === "processing";

              return (
                <article
                  className={[
                    "document-card",
                    needsAttention ? "document-card--danger" : "document-card--default",
                  ].join(" ")}
                  key={document.id}
                >
                  <div className="document-card__header">
                    <div>
                      <h4>{document.file_name}</h4>
                      <p>
                        {formatDocumentType(document.document_type)} · updated {formatDate(document.updated_at)}
                      </p>
                    </div>
                    <div className="document-card__signals">
                      {document.validation_flag_count > 0 ? (
                        <span className="signal-pill signal-pill--danger">
                          {document.validation_flag_count} flag{document.validation_flag_count > 1 ? "s" : ""}
                        </span>
                      ) : (
                        <span className="signal-pill signal-pill--neutral">No flags</span>
                      )}
                      <StatusBadge status={document.status} />
                    </div>
                  </div>

                  <div className="document-card__meta">
                    <span className="signal-pill signal-pill--soft">
                      {formatStatusLabel(document.status)}
                    </span>
                    <span className="signal-pill signal-pill--soft">
                      {formatDocumentType(document.document_type)}
                    </span>
                  </div>

                  <ProgressMeter
                    label="Pipeline progress"
                    tone={needsAttention ? "warning" : document.status === "approved" ? "positive" : "brand"}
                    value={STATUS_PROGRESS[document.status]}
                  />

                  <div className="document-card__actions">
                    <button
                      className="button button-secondary"
                      disabled={processDisabled}
                      onClick={() => void onProcess(document.id)}
                      type="button"
                    >
                      {processDisabled ? "Processing..." : document.status === "uploaded" ? "Run AI scan" : "Reprocess"}
                    </button>
                    <Link
                      className={`button ${needsAttention ? "button-primary" : "button-secondary"}`}
                      href={`/review/${document.id}`}
                    >
                      Open review
                    </Link>
                  </div>
                </article>
              );
            })}
          </div>
        </section>
      ))}
    </div>
  );
}
