"use client";

import { useRef, useState } from "react";

import { PipelineStrip } from "@/components/common/pipeline-strip";
import { buttonStyles, feedbackError, inverseEyebrow, signalPillStyles } from "@/components/common/ui";
import { cn } from "@/lib/utils";

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
    <div className="grid gap-5">
      <label
        className={cn(
          "grid gap-3 rounded-[32px] border border-dashed p-6 text-left transition duration-200",
          busy
            ? "border-[#9fe870]/50 bg-[#9fe870]/10"
            : "border-black/[0.12] bg-[linear-gradient(135deg,rgba(255,255,255,0.84),rgba(255,255,255,0.66)),linear-gradient(180deg,rgba(159,232,112,0.08),transparent_70%)] hover:border-[#9fe870]/40 hover:bg-white/90",
        )}
      >
        <span className={inverseEyebrow.replace("text-white/65", "text-[#6c7268]")}>Document intake</span>
        <strong>Drop or browse ID cards, payslips, and bank statements.</strong>
        <span className="text-sm leading-6 text-[#454745]">
          Raw files stay preserved. OCR and extraction artifacts are tracked separately.
        </span>
        <input
          className="text-sm text-[#454745] file:mr-4 file:rounded-full file:border-0 file:bg-[#9fe870] file:px-4 file:py-2 file:font-semibold file:text-[#163300]"
          ref={inputRef}
          accept=".png,.jpg,.jpeg,.pdf"
          multiple
          onChange={(event) => setSelectedFiles(Array.from(event.target.files || []))}
          type="file"
        />
      </label>

      <div className="flex flex-wrap items-center gap-3">
        <span className={signalPillStyles("soft")}>.jpg</span>
        <span className={signalPillStyles("soft")}>.jpeg</span>
        <span className={signalPillStyles("soft")}>.png</span>
        <span className={signalPillStyles("soft")}>.pdf</span>
      </div>

      {selectedFiles.length > 0 ? (
        <div className="grid gap-3">
          {selectedFiles.map((file) => (
            <div
              className="flex items-center justify-between gap-3 rounded-[22px] border border-black/10 bg-white/[0.78] px-4 py-3"
              key={`${file.name}-${file.lastModified}`}
            >
              <strong>{file.name}</strong>
              <span className="text-sm text-[#454745]">{Math.max(1, Math.round(file.size / 1024))} KB</span>
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

      <button className={buttonStyles("primary", "justify-center")} disabled={busy} onClick={handleUpload} type="button">
        {busy ? "Uploading..." : "Upload Documents"}
      </button>
      {error ? <p className={feedbackError}>{error}</p> : null}
    </div>
  );
}
