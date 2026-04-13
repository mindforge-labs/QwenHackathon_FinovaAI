"use client";

import Link from "next/link";
import { use } from "react";

import { ReviewEditor } from "@/components/review/review-editor";
import { StatusBadge } from "@/components/common/status-badge";
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
      <section className="hero hero--review">
        <div className="hero__content">
          <p className="eyebrow">Review workspace</p>
          <h1>{document ? document.file_name : "Correct the hard cases before they become loan risk."}</h1>
          <p>
            Inspect document evidence, compare AI output against reviewer corrections, and make an
            explicit decision with a visible audit trail.
          </p>
          {document ? (
            <div className="hero__meta">
              <span>{formatDocumentType(document.document_type)}</span>
              <span>Updated {formatDate(document.updated_at)}</span>
            </div>
          ) : null}
          <div className="hero__actions">
            <Link className="button button-secondary" href={document ? `/applications/${document.application_id}` : "/applications"}>
              Back to application
            </Link>
          </div>
        </div>

        <aside className="hero__panel">
          <div className="hero__panel-header">
            <div>
              <p className="eyebrow">Decision context</p>
              <h2>Human-in-the-loop lane</h2>
            </div>
            {document ? <StatusBadge status={document.status} /> : null}
          </div>
          <p className="hero__panel-copy">
            The workspace below turns OCR, extraction confidence, and validation flags into a concrete
            review decision.
          </p>
        </aside>
      </section>

      {loading ? <p>Loading document...</p> : null}
      {error ? <p className="feedback feedback-error">{error}</p> : null}
      {document ? <ReviewEditor document={document} onRefresh={refresh} /> : null}
    </>
  );
}
