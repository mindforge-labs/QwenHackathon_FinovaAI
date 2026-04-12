"use client";

import Link from "next/link";
import { use } from "react";

import { SectionCard } from "@/components/common/section-card";
import { StatusBadge } from "@/components/common/status-badge";
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

  return (
    <>
      <section className="hero">
        <h1>Keep the intake moving without losing the review trail.</h1>
        <p>
          Upload one or more files, trigger processing, then jump straight into the review screen for
          low-confidence or flagged documents.
        </p>
      </section>

      <div className="dashboard-grid">
        <SectionCard title="Application Detail" subtitle="Track document readiness and send new files into the pipeline.">
          {loading ? <p>Loading application...</p> : null}
          {error ? <p className="feedback feedback-error">{error}</p> : null}
          {application ? (
            <>
              <div className="application-card">
                <div>
                  <h3>{application.applicant_name || "Untitled application"}</h3>
                  <p>{application.email || application.phone || "No contact info yet"}</p>
                  <p>{formatDate(application.created_at)}</p>
                </div>
                <StatusBadge status={application.status} />
              </div>
              <UploadForm onUpload={upload} />
              <button className="button button-secondary" onClick={() => void refresh()} type="button">
                Refresh
              </button>
            </>
          ) : null}
        </SectionCard>

        <SectionCard title="Documents" subtitle="Process a file, inspect status, or open the review workspace.">
          {application ? (
            <DocumentList documents={application.documents} onProcess={triggerProcessing} />
          ) : (
            <p>No documents yet.</p>
          )}
          <div className="button-row">
            <Link className="button button-secondary" href="/applications">
              Back to Applications
            </Link>
          </div>
        </SectionCard>
      </div>
    </>
  );
}
