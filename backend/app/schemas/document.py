from __future__ import annotations

from datetime import datetime

from app.schemas.common import DocumentStatus, ORMModel
from app.schemas.extraction import ExtractionRead
from app.schemas.review import ReviewActionRead
from app.schemas.validation import ValidationFlagRead


class DocumentSummary(ORMModel):
    id: str
    file_name: str
    mime_type: str
    document_type: str | None = None
    status: DocumentStatus
    validation_flag_count: int = 0
    created_at: datetime
    updated_at: datetime


class DocumentUploadResponse(ORMModel):
    document_id: str
    upload_status: DocumentStatus


class DocumentProcessResponse(ORMModel):
    document_id: str
    processing_status: DocumentStatus
    page_count: int


class DocumentPageMetadata(ORMModel):
    id: str
    page_number: int
    raw_image_storage_key: str
    processed_image_storage_key: str
    ocr_text: str | None = None


class DocumentPagesResponse(ORMModel):
    document_id: str
    items: list[DocumentPageMetadata]


class DocumentDetail(ORMModel):
    id: str
    application_id: str
    file_name: str
    mime_type: str
    storage_key: str
    document_type: str | None = None
    status: DocumentStatus
    page_count: int
    quality_score: float | None = None
    ocr_confidence: float | None = None
    extraction_confidence: float | None = None
    created_at: datetime
    updated_at: datetime
    pages: list[DocumentPageMetadata]
    extraction: ExtractionRead | None = None
    validation_flags: list[ValidationFlagRead]
    review_actions: list[ReviewActionRead] = []
