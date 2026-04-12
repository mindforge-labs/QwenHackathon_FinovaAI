"use client";

import Link from "next/link";

import { StatusBadge } from "@/components/common/status-badge";
import { DocumentSummary } from "@/lib/types";

export function DocumentList({
  documents,
  onProcess,
}: {
  documents: DocumentSummary[];
  onProcess: (documentId: string) => Promise<void>;
}) {
  return (
    <div className="document-list">
      {documents.map((document) => (
        <article className="document-row" key={document.id}>
          <div>
            <h3>{document.file_name}</h3>
            <p>{document.document_type || "unknown document type"}</p>
            <p>{document.validation_flag_count} warning(s)</p>
          </div>
          <div className="document-row__actions">
            <StatusBadge status={document.status} />
            <button className="button button-secondary" onClick={() => void onProcess(document.id)} type="button">
              Process
            </button>
            <Link className="button button-secondary" href={`/review/${document.id}`}>
              Review
            </Link>
          </div>
        </article>
      ))}
    </div>
  );
}
