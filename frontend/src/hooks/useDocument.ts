"use client";

import { useEffect, useState } from "react";

import { getApplication, getDocument, processDocument, uploadDocument } from "@/lib/api";
import { ApplicationDetail, DocumentDetail } from "@/lib/types";

export function useApplicationDetail(applicationId: string) {
  const [application, setApplication] = useState<ApplicationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      setApplication(await getApplication(applicationId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load application.");
    } finally {
      setLoading(false);
    }
  }

  async function upload(files: FileList | File[]) {
    const list = Array.from(files);
    for (const file of list) {
      await uploadDocument(applicationId, file);
    }
    await refresh();
  }

  async function triggerProcessing(documentId: string) {
    await processDocument(documentId);
    await refresh();
  }

  useEffect(() => {
    void refresh();
  }, [applicationId]);

  return { application, loading, error, refresh, upload, triggerProcessing };
}

export function useDocumentDetail(documentId: string) {
  const [document, setDocument] = useState<DocumentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      setDocument(await getDocument(documentId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load document.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
  }, [documentId]);

  return { document, loading, error, refresh };
}
