"use client";

import { useState } from "react";

import { submitDecision, updateReview } from "@/lib/api";

export function useReview(documentId: string, onSuccess: () => Promise<void> | void) {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function saveCorrection(payload: {
    reviewer_name: string;
    comment?: string;
    corrected_json: Record<string, unknown>;
  }) {
    setSubmitting(true);
    setError(null);
    try {
      await updateReview(documentId, payload);
      await onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save review changes.");
    } finally {
      setSubmitting(false);
    }
  }

  async function decide(payload: {
    reviewer_name: string;
    action: "approve" | "reject" | "request_reupload";
    comment?: string;
  }) {
    setSubmitting(true);
    setError(null);
    try {
      await submitDecision(documentId, payload);
      await onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not submit decision.");
    } finally {
      setSubmitting(false);
    }
  }

  return { submitting, error, saveCorrection, decide };
}
