"use client";

import Link from "next/link";

import { ProgressMeter } from "@/components/common/progress-meter";
import { StatusBadge } from "@/components/common/status-badge";
import { buttonStyles, emptyState, eyebrow, signalPillStyles } from "@/components/common/ui";
import { cn } from "@/lib/utils";
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
    return <p className={emptyState}>No documents uploaded yet.</p>;
  }

  return (
    <div className="grid gap-6">
      {groups.map((group) => (
        <section className="grid gap-4" key={group.key}>
          <header className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className={eyebrow}>{group.title}</p>
              <h3 className="mt-2 text-[1.6rem] font-semibold tracking-[-0.03em] text-[#0e0f0c]">
                {group.items.length} document(s)
              </h3>
            </div>
            <p className="max-w-2xl text-sm leading-6 text-[#454745]">{group.subtitle}</p>
          </header>

          <div className="grid gap-4">
            {group.items.map((document) => {
              const needsAttention =
                document.validation_flag_count > 0 ||
                document.status === "needs_review" ||
                document.status === "failed" ||
                document.status === "rejected";
              const processDisabled = document.status === "processing";

              return (
                <article
                  className={cn(
                    "rounded-[30px] border bg-white/[0.82] p-5 shadow-[0_0_0_1px_rgba(14,15,12,0.04)]",
                    needsAttention ? "border-[#d03238]/[0.18]" : "border-black/10",
                  )}
                  key={document.id}
                >
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <h4 className="text-[1.2rem] font-semibold tracking-[-0.03em] text-[#0e0f0c]">{document.file_name}</h4>
                      <p className="mt-2 text-sm leading-6 text-[#454745]">
                        {formatDocumentType(document.document_type)} · updated {formatDate(document.updated_at)}
                      </p>
                    </div>
                    <div className="flex flex-wrap items-center gap-3">
                      {document.validation_flag_count > 0 ? (
                        <span className={signalPillStyles("danger")}>
                          {document.validation_flag_count} flag{document.validation_flag_count > 1 ? "s" : ""}
                        </span>
                      ) : (
                        <span className={signalPillStyles("neutral")}>No flags</span>
                      )}
                      <StatusBadge status={document.status} />
                    </div>
                  </div>

                  <div className="mt-4 flex flex-wrap items-center gap-3">
                    <span className={signalPillStyles("soft")}>
                      {formatStatusLabel(document.status)}
                    </span>
                    <span className={signalPillStyles("soft")}>
                      {formatDocumentType(document.document_type)}
                    </span>
                  </div>

                  <div className="mt-5">
                    <ProgressMeter
                    label="Pipeline progress"
                    tone={needsAttention ? "warning" : document.status === "approved" ? "positive" : "brand"}
                    value={STATUS_PROGRESS[document.status]}
                  />
                  </div>

                  <div className="mt-5 flex flex-wrap items-center gap-3">
                    <button
                      className={buttonStyles("secondary")}
                      disabled={processDisabled}
                      onClick={() => void onProcess(document.id)}
                      type="button"
                    >
                      {processDisabled ? "Processing..." : document.status === "uploaded" ? "Run AI scan" : "Reprocess"}
                    </button>
                    <Link
                      className={buttonStyles(needsAttention ? "primary" : "secondary")}
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
