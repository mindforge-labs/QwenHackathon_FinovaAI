"use client";

import Link from "next/link";
import { use } from "react";

import { ReviewEditor } from "@/components/review/review-editor";
import { SectionCard } from "@/components/common/section-card";
import { useDocumentDetail } from "@/hooks/useDocument";

export default function ReviewPage({
  params,
}: {
  params: Promise<{ documentId: string }>;
}) {
  const { documentId } = use(params);
  const { document, loading, error, refresh } = useDocumentDetail(documentId);

  return (
    <>
      <section className="hero">
        <h1>Correct the hard cases before they become loan risk.</h1>
        <p>
          Edit structured extraction, inspect warnings, and keep a full review history for every
          decision taken on a document.
        </p>
      </section>

      <SectionCard title="Review Workspace" subtitle="Preview the document and push the final decision back to the backend.">
        {loading ? <p>Loading document...</p> : null}
        {error ? <p className="feedback feedback-error">{error}</p> : null}
        {document ? <ReviewEditor document={document} onRefresh={refresh} /> : null}
        <div className="button-row">
          <Link className="button button-secondary" href={document ? `/applications/${document.application_id}` : "/applications"}>
            Back to Application
          </Link>
        </div>
      </SectionCard>
    </>
  );
}
