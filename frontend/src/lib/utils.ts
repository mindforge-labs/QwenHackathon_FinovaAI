import { DocumentStatus } from "@/lib/types";

export function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-GB", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function formatStatusLabel(status: string): string {
  return status.replace(/_/g, " ");
}

export function isDecisionReady(status: DocumentStatus): boolean {
  return status === "processed" || status === "needs_review" || status === "approved";
}

export function apiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
}
