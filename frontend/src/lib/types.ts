export type DocumentStatus =
  | "uploaded"
  | "processing"
  | "processed"
  | "needs_review"
  | "approved"
  | "rejected"
  | "failed";

export type ApplicationStatus =
  | "draft"
  | "processing"
  | "under_review"
  | "approved"
  | "rejected";

export type ValidationFlag = {
  id: string;
  flag_code: string;
  severity: "warning" | "error";
  message: string;
  field_name: string | null;
  created_at: string;
};

export type ReviewAction = {
  id: string;
  reviewer_name: string;
  action: string;
  comment: string | null;
  corrected_json: Record<string, unknown> | null;
  created_at: string;
};

export type ExtractionRecord = {
  id: string;
  schema_version: string;
  raw_extraction_json: Record<string, unknown>;
  normalized_extraction_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type DocumentSummary = {
  id: string;
  file_name: string;
  mime_type: string;
  document_type: string | null;
  status: DocumentStatus;
  page_count: number;
  validation_flag_count: number;
  quality_score: number | null;
  ocr_confidence: number | null;
  extraction_confidence: number | null;
  requires_attention: boolean;
  review_action_count: number;
  created_at: string;
  updated_at: string;
};

export type ApplicationSummary = {
  id: string;
  applicant_name: string | null;
  phone: string | null;
  email: string | null;
  status: ApplicationStatus;
  document_count: number;
  processed_document_count: number;
  flagged_document_count: number;
  approved_document_count: number;
  latest_document_updated_at: string | null;
  next_review_document_id: string | null;
  next_review_document_file_name: string | null;
  next_review_document_updated_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ApplicationDetail = ApplicationSummary & {
  documents: DocumentSummary[];
};

export type OCRLine = {
  text: string;
  bbox: number[][];
  confidence: number;
};

export type DocumentPage = {
  id: string;
  page_number: number;
  raw_image_storage_key: string;
  processed_image_storage_key: string;
  ocr_text: string | null;
  ocr_confidence: number | null;
  ocr_lines: OCRLine[];
};

export type DocumentFieldSignal = {
  field_name: string;
  value: unknown;
  page_number: number | null;
  bbox: number[][] | null;
  confidence: number | null;
  is_flagged: boolean;
  is_missing: boolean;
  source: "ocr_line_match" | "derived" | "missing";
  matched_text: string | null;
};

export type DocumentTimelineEvent = {
  code: string;
  label: string;
  description: string;
  tone: "neutral" | "positive" | "warning" | "danger" | "pending";
  created_at: string | null;
};

export type DocumentDetail = {
  id: string;
  application_id: string;
  file_name: string;
  mime_type: string;
  storage_key: string;
  document_type: string | null;
  status: DocumentStatus;
  page_count: number;
  quality_score: number | null;
  ocr_confidence: number | null;
  extraction_confidence: number | null;
  created_at: string;
  updated_at: string;
  pages: DocumentPage[];
  extraction: ExtractionRecord | null;
  validation_flags: ValidationFlag[];
  review_actions: ReviewAction[];
  field_signals: DocumentFieldSignal[];
  timeline: DocumentTimelineEvent[];
};

export type ApplicationsResponse = {
  items: ApplicationSummary[];
};

export type DocumentPagesResponse = {
  document_id: string;
  items: DocumentPage[];
};

export type ReviewUpdateResponse = {
  document_id: string;
  status: DocumentStatus;
  extraction: ExtractionRecord;
  review_action: ReviewAction;
};

export type ReviewDecisionResponse = {
  document_id: string;
  status: DocumentStatus;
  review_action: ReviewAction;
};
