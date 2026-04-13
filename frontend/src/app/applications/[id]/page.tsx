"use client";

import Link from "next/link";
import { use } from "react";

import { MetricCard } from "@/components/common/metric-card";
import { PipelineStrip } from "@/components/common/pipeline-strip";
import { SectionCard } from "@/components/common/section-card";
import { DocumentList } from "@/components/document/document-list";
import { UploadForm } from "@/components/upload/upload-form";
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
      <section className="hero hero--detail">
        <div className="hero__content">
          <p className="eyebrow">Application detail</p>
          <h1>{application?.applicant_name || "Untitled application"}</h1>
          <p>
            Keep the intake moving without losing review context. Upload files, trigger the AI pipeline,
            and jump directly into the cases where confidence drops or risk signals appear.
          </p>
          {application ? (
            <div className="hero__meta">
              <span>{application.email || application.phone || "No contact info yet"}</span>
              <span>Created {formatDate(application.created_at)}</span>
            </div>
          ) : null}
          <div className="hero__actions">
            <Link className="button button-secondary" href="/applications">
              Back to applications
            </Link>
            {reviewCandidate ? (
              <Link className="button button-primary" href={`/review/${reviewCandidate.id}`}>
                Open next review
              </Link>
            ) : null}
          </div>
        </div>

        <aside className="hero__panel">
          <div className="hero__panel-header">
            <div>
              <p className="eyebrow">Case flow</p>
              <h2>Upload to approval</h2>
            </div>
          </div>
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
        </aside>
      </section>

      <section className="metric-grid">
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

      <div className="dashboard-grid dashboard-grid--detail">
        <div className="dashboard-sidebar">
          <SectionCard
            actions={
              <button className="button button-secondary" onClick={() => void refresh()} type="button">
                Refresh
              </button>
            }
            eyebrow="Upload"
            subtitle="Send new files into the processing pipeline while keeping the raw evidence intact."
            title="Add documents"
          >
          {loading ? <p>Loading application...</p> : null}
          {error ? <p className="feedback feedback-error">{error}</p> : null}
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
            <div className="quick-action-grid">
              <button className="button button-secondary" onClick={() => void refresh()} type="button">
                Sync latest pipeline state
              </button>
              {reviewCandidate ? (
                <Link className="button button-primary" href={`/review/${reviewCandidate.id}`}>
                  Review flagged document
                </Link>
              ) : (
                <span className="empty-state">No review-ready document yet.</span>
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
            <p className="empty-state">No documents yet.</p>
          )}
        </SectionCard>
      </div>
    </>
  );
}
