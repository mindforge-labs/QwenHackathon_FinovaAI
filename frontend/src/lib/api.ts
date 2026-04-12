import {
  ApplicationDetail,
  ApplicationsResponse,
  DocumentDetail,
  ReviewDecisionResponse,
  ReviewUpdateResponse,
} from "@/lib/types";
import { apiBaseUrl } from "@/lib/utils";

const API_BASE_URL = apiBaseUrl();

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function listApplications(): Promise<ApplicationsResponse> {
  return request<ApplicationsResponse>("/applications");
}

export async function createApplication(payload: {
  applicant_name?: string;
  phone?: string;
  email?: string;
}): Promise<ApplicationDetail> {
  return request<ApplicationDetail>("/applications", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getApplication(applicationId: string): Promise<ApplicationDetail> {
  return request<ApplicationDetail>(`/applications/${applicationId}`);
}

export async function uploadDocument(applicationId: string, file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/applications/${applicationId}/documents`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<{ document_id: string; upload_status: string }>;
}

export async function processDocument(documentId: string) {
  return request<{ document_id: string; processing_status: string; page_count: number }>(
    `/documents/${documentId}/process`,
    { method: "POST" },
  );
}

export async function getDocument(documentId: string): Promise<DocumentDetail> {
  return request<DocumentDetail>(`/documents/${documentId}`);
}

export async function updateReview(
  documentId: string,
  payload: {
    reviewer_name: string;
    comment?: string;
    corrected_json: Record<string, unknown>;
  },
): Promise<ReviewUpdateResponse> {
  return request<ReviewUpdateResponse>(`/documents/${documentId}/review`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function submitDecision(
  documentId: string,
  payload: {
    reviewer_name: string;
    action: "approve" | "reject" | "request_reupload";
    comment?: string;
  },
): Promise<ReviewDecisionResponse> {
  return request<ReviewDecisionResponse>(`/documents/${documentId}/decision`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function documentAssetUrl(documentId: string): string {
  return `${API_BASE_URL}/documents/${documentId}/content`;
}

export function documentPageAssetUrl(
  documentId: string,
  pageNumber: number,
  variant: "raw" | "processed" = "processed",
): string {
  return `${API_BASE_URL}/documents/${documentId}/pages/${pageNumber}/content?variant=${variant}`;
}
