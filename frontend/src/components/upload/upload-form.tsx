"use client";

import { useRef, useState } from "react";

import { PipelineStrip } from "@/components/common/pipeline-strip";

export function UploadForm({
  onUpload,
}: {
  onUpload: (files: FileList) => Promise<void>;
}) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  async function handleUpload() {
    const files = inputRef.current?.files;
    if (!files || files.length === 0) {
      setError("Choose at least one file to upload.");
      return;
    }

    setBusy(true);
    setError(null);
    try {
      await onUpload(files);
      if (inputRef.current) {
        inputRef.current.value = "";
      }
      setSelectedFiles([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="upload-form">
      <label className={`upload-dropzone ${busy ? "upload-dropzone--busy" : ""}`}>
        <span className="upload-dropzone__eyebrow">Document intake</span>
        <strong>Drop or browse ID cards, payslips, and bank statements.</strong>
        <span>Raw files stay preserved. OCR and extraction artifacts are tracked separately.</span>
        <input
          ref={inputRef}
          accept=".png,.jpg,.jpeg,.pdf"
          multiple
          onChange={(event) => setSelectedFiles(Array.from(event.target.files || []))}
          type="file"
        />
      </label>

      <div className="upload-supported-types">
        <span className="signal-pill signal-pill--soft">.jpg</span>
        <span className="signal-pill signal-pill--soft">.jpeg</span>
        <span className="signal-pill signal-pill--soft">.png</span>
        <span className="signal-pill signal-pill--soft">.pdf</span>
      </div>

      {selectedFiles.length > 0 ? (
        <div className="upload-file-list">
          {selectedFiles.map((file) => (
            <div className="upload-file-list__item" key={`${file.name}-${file.lastModified}`}>
              <strong>{file.name}</strong>
              <span>{Math.max(1, Math.round(file.size / 1024))} KB</span>
            </div>
          ))}
        </div>
      ) : null}

      <PipelineStrip
        compact
        steps={[
          {
            label: "Upload",
            description: selectedFiles.length > 0 ? `${selectedFiles.length} file(s) staged` : "Awaiting files",
            state: selectedFiles.length > 0 ? "done" : "pending",
          },
          {
            label: "OCR",
            description: busy ? "Preparing OCR queue" : "PaddleOCR will run after upload",
            state: busy ? "active" : "pending",
          },
          {
            label: "AI extraction",
            description: busy ? "Parsing structured fields" : "LLM/rule extraction after OCR",
            state: busy ? "active" : "pending",
          },
          {
            label: "Risk review",
            description: "Flagged documents are routed to manual review",
            state: selectedFiles.length > 0 || busy ? "warning" : "pending",
          },
        ]}
      />

      <button className="button button-primary" disabled={busy} onClick={handleUpload} type="button">
        {busy ? "Uploading..." : "Upload Documents"}
      </button>
      {error ? <p className="feedback feedback-error">{error}</p> : null}
    </div>
  );
}
