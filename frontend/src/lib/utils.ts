import { DocumentStatus } from "@/lib/types";

export function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-GB", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function formatStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    uploaded: "Uploaded",
    processing: "Processing",
    processed: "Processed",
    needs_review: "Needs review",
    approved: "Approved",
    rejected: "Rejected",
    failed: "Failed",
    draft: "Draft",
    under_review: "Under review",
  };

  if (labels[status]) {
    return labels[status];
  }

  return status
    .replace(/_/g, " ")
    .split(" ")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function isDecisionReady(status: DocumentStatus): boolean {
  return status === "processed" || status === "needs_review" || status === "approved";
}

export function apiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
}

export function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }

  return `${Math.round(value * 100)}%`;
}

export function formatDocumentType(value: string | null | undefined): string {
  const labels: Record<string, string> = {
    id_card: "ID card",
    payslip: "Payslip",
    bank_statement: "Bank statement",
    unknown: "Unknown type",
  };

  if (!value) {
    return "Unknown type";
  }

  return labels[value] || value.replace(/_/g, " ");
}
