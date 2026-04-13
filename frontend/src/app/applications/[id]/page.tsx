"use client";

import Link from "next/link";
import { use } from "react";

import { MetricCard } from "@/components/common/metric-card";
import { PipelineStrip } from "@/components/common/pipeline-strip";
import { SectionCard } from "@/components/common/section-card";
import { DocumentList } from "@/components/document/document-list";
import { UploadForm } from "@/components/upload/upload-form";
import {
  buttonStyles,
  displayFont,
  emptyState,
  eyebrow,
  feedbackError,
  inverseEyebrow,
  sectionCardDark,
} from "@/components/common/ui";
import { useApplicationDetail } from "@/hooks/useDocument";
import { formatDate } from "@/lib/utils";

export default function ApplicationDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { application, loading, error, upload, triggerProcessing, refresh } = useApplicationDetail(id);
  const reviewCandidate = application?.documents
    .filter(
      (document) =>
        document.status === "needs_review" ||
        document.validation_flag_count > 0 ||
        document.status === "processed",
    )
    .sort((left, right) => Date.parse(right.updated_at) - Date.parse(left.updated_at))[0];
  const documentCount = application?.documents.length || 0;
  const processingCount =
    application?.documents.filter((document) => document.status === "processing" || document.status === "uploaded").length || 0;
  const riskCount =
    application?.documents.filter(
      (document) =>
        document.validation_flag_count > 0 ||
        document.status === "needs_review" ||
        document.status === "failed" ||
        document.status === "rejected",
    ).length || 0;
  const approvedCount =
    application?.documents.filter((document) => document.status === "approved").length || 0;

  return (
    <>
      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(320px,0.95fr)]">
        <div className="rounded-[40px] border border-black/[0.12] bg-[linear-gradient(135deg,rgba(255,255,255,0.88),rgba(255,255,255,0.72)),linear-gradient(180deg,rgba(159,232,112,0.08),transparent_60%)] p-[34px] shadow-[0_0_0_1px_rgba(14,15,12,0.04)]">
          <p className={eyebrow}>Application detail</p>
          <h1 className={`${displayFont} mt-4 text-[clamp(3.6rem,7.8vw,6.75rem)] text-[#0e0f0c]`}>
            {application?.applicant_name || "Untitled application"}
          </h1>
          <p className="mt-5 max-w-[62ch] text-[1.08rem] leading-8 text-[#454745]">
            Keep the intake moving without losing review context. Upload files, trigger the AI pipeline,
            and jump directly into the cases where confidence drops or risk signals appear.
          </p>
          {application ? (
            <div className="mt-[18px] flex flex-wrap gap-3 text-[0.92rem] text-[#6c7268]">
              <span>{application.email || application.phone || "No contact info yet"}</span>
              <span>Created {formatDate(application.created_at)}</span>
            </div>
          ) : null}
          <div className="mt-7 flex flex-wrap items-center gap-3">
            <Link className={buttonStyles("secondary")} href="/applications">
              Back to applications
            </Link>
            {reviewCandidate ? (
              <Link className={buttonStyles("primary")} href={`/review/${reviewCandidate.id}`}>
                Open next review
              </Link>
            ) : null}
          </div>
        </div>

        <aside className={sectionCardDark}>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className={inverseEyebrow}>Case flow</p>
              <h2 className={`${displayFont} mt-2 text-[clamp(2rem,3.8vw,3.2rem)] text-[#ecf3e2]`}>
                Upload to approval
              </h2>
            </div>
          </div>
          <div className="mt-6">
            <PipelineStrip
            compact
            steps={[
              {
                label: "Upload",
                description: documentCount > 0 ? `${documentCount} file(s) attached` : "Awaiting documents",
                state: documentCount > 0 ? "done" : "pending",
              },
              {
                label: "OCR",
                description: processingCount > 0 ? "OCR is active for in-flight files" : "OCR ready",
                state: processingCount > 0 ? "active" : documentCount > 0 ? "done" : "pending",
              },
              {
                label: "AI extraction",
                description: documentCount > 0 ? "Structured fields and confidences available in review" : "No extraction yet",
                state: documentCount > 0 ? "done" : "pending",
              },
              {
                label: "Risk review",
                description: riskCount > 0 ? `${riskCount} document(s) need attention` : "Queue is clean",
                state: riskCount > 0 ? "warning" : documentCount > 0 ? "done" : "pending",
              },
            ]}
          />
          </div>
        </aside>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          detail="Documents attached to this application"
          label="Total documents"
          tone="neutral"
          value={String(documentCount)}
        />
        <MetricCard
          detail="Files currently in upload/OCR/extraction"
          label="In flight"
          tone="warning"
          value={String(processingCount)}
        />
        <MetricCard
          detail="Documents with flags or manual review pressure"
          label="Risk signals"
          tone="danger"
          value={String(riskCount)}
        />
        <MetricCard
          detail="Documents already cleared by a reviewer"
          label="Approved docs"
          tone="positive"
          value={String(approvedCount)}
        />
      </section>

      <div className="grid gap-6 xl:grid-cols-[360px_minmax(0,1fr)]">
        <div className="grid gap-6">
          <SectionCard
            actions={
              <button className={buttonStyles("secondary")} onClick={() => void refresh()} type="button">
                Refresh
              </button>
            }
            eyebrow="Upload"
            subtitle="Send new files into the processing pipeline while keeping the raw evidence intact."
            title="Add documents"
          >
          {loading ? <p>Loading application...</p> : null}
          {error ? <p className={feedbackError}>{error}</p> : null}
          {application ? (
            <>
              <UploadForm onUpload={upload} />
            </>
          ) : null}
        </SectionCard>

          <SectionCard
            eyebrow="Shortcuts"
            subtitle="Use these to drive the demo path through processing and manual review."
            title="Case actions"
          >
            <div className="grid gap-4">
              <button className={buttonStyles("secondary", "justify-center")} onClick={() => void refresh()} type="button">
                Sync latest pipeline state
              </button>
              {reviewCandidate ? (
                <Link className={buttonStyles("primary", "justify-center")} href={`/review/${reviewCandidate.id}`}>
                  Review flagged document
                </Link>
              ) : (
                <span className={emptyState}>No review-ready document yet.</span>
              )}
            </div>
          </SectionCard>
        </div>

        <SectionCard
          eyebrow="Documents"
          subtitle="Track readiness, re-run processing, and open the review workspace from the same queue."
          title="Application documents"
        >
          {application ? (
            <DocumentList documents={application.documents} onProcess={triggerProcessing} />
          ) : (
            <p className={emptyState}>No documents yet.</p>
          )}
        </SectionCard>
      </div>
    </>
  );
}
