"use client";

import { useRef, useState } from "react";

export function UploadForm({
  onUpload,
}: {
  onUpload: (files: FileList) => Promise<void>;
}) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="upload-form">
      <input ref={inputRef} type="file" accept=".png,.jpg,.jpeg,.pdf" multiple />
      <button className="button button-primary" disabled={busy} onClick={handleUpload} type="button">
        {busy ? "Uploading..." : "Upload Documents"}
      </button>
      {error ? <p className="feedback feedback-error">{error}</p> : null}
    </div>
  );
}
