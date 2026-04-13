"use client";

import Link from "next/link";
import { use } from "react";

import { ReviewEditor } from "@/components/review/review-editor";
import { StatusBadge } from "@/components/common/status-badge";
import { buttonStyles, displayFont, eyebrow, feedbackError, sectionCard } from "@/components/common/ui";
import { useDocumentDetail } from "@/hooks/useDocument";
import { formatDate, formatDocumentType } from "@/lib/utils";

export default function ReviewPage({
  params,
}: {
  params: Promise<{ documentId: string }>;
}) {
  const { documentId } = use(params);
  const { document, loading, error, refresh } = useDocumentDetail(documentId);

  return (
    <>
      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(320px,0.95fr)]">
        <div className="rounded-[40px] border border-black/[0.12] bg-[linear-gradient(135deg,rgba(255,255,255,0.88),rgba(255,255,255,0.72)),linear-gradient(180deg,rgba(159,232,112,0.08),transparent_60%)] p-[34px] shadow-[0_0_0_1px_rgba(14,15,12,0.04)]">
          <p className={eyebrow}>Review workspace</p>
          <h1 className={`${displayFont} mt-4 text-[clamp(3.6rem,7.8vw,6.75rem)] text-[#0e0f0c]`}>
            {document ? document.file_name : "Correct the hard cases before they become loan risk."}
          </h1>
          <p className="mt-5 max-w-[62ch] text-[1.08rem] leading-8 text-[#454745]">
            Inspect document evidence, compare AI output against reviewer corrections, and make an
            explicit decision with a visible audit trail.
          </p>
          {document ? (
            <div className="mt-[18px] flex flex-wrap gap-3 text-[0.92rem] text-[#6c7268]">
              <span>{formatDocumentType(document.document_type)}</span>
              <span>Updated {formatDate(document.updated_at)}</span>
            </div>
          ) : null}
          <div className="mt-7 flex flex-wrap items-center gap-3">
            <Link className={buttonStyles("secondary")} href={document ? `/applications/${document.application_id}` : "/applications"}>
              Back to application
            </Link>
          </div>
        </div>

        <aside className={sectionCard}>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className={eyebrow}>Decision context</p>
              <h2 className={`${displayFont} mt-2 text-[clamp(2rem,3.8vw,3.2rem)] text-[#0e0f0c]`}>
                Human-in-the-loop lane
              </h2>
            </div>
            {document ? <StatusBadge status={document.status} /> : null}
          </div>
          <p className="mt-[18px] leading-7 text-[#454745]">
            The workspace below turns OCR, extraction confidence, and validation flags into a concrete
            review decision.
          </p>
        </aside>
      </section>

      {loading ? <p>Loading document...</p> : null}
      {error ? <p className={feedbackError}>{error}</p> : null}
      {document ? <ReviewEditor document={document} onRefresh={refresh} /> : null}
    </>
  );
}
