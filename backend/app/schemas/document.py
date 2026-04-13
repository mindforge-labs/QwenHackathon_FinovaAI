from __future__ import annotations

from typing import Any, Literal
from datetime import datetime

from pydantic import Field

from app.schemas.common import DocumentStatus, ORMModel
from app.schemas.extraction import ExtractionRead
from app.schemas.review import ReviewActionRead
from app.schemas.validation import ValidationFlagRead


class OCRLineRead(ORMModel):
    text: str
    bbox: list[list[float]]
    confidence: float


class DocumentSummary(ORMModel):
    id: str
    file_name: str
    mime_type: str
    document_type: str | None = None
    status: DocumentStatus
    page_count: int = 0
    validation_flag_count: int = 0
    quality_score: float | None = None
    ocr_confidence: float | None = None
    extraction_confidence: float | None = None
    requires_attention: bool = False
    review_action_count: int = 0
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
    ocr_confidence: float | None = None
    ocr_lines: list[OCRLineRead] = Field(default_factory=list)


class DocumentPagesResponse(ORMModel):
    document_id: str
    items: list[DocumentPageMetadata]


class DocumentFieldSignal(ORMModel):
    field_name: str
    value: Any = None
    page_number: int | None = None
    bbox: list[list[float]] | None = None
    confidence: float | None = None
    is_flagged: bool = False
    is_missing: bool = False
    source: Literal["ocr_line_match", "derived", "missing"]
    matched_text: str | None = None


class DocumentTimelineEvent(ORMModel):
    code: str
    label: str
    description: str
    tone: Literal["neutral", "positive", "warning", "danger", "pending"]
    created_at: datetime | None = None


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
    field_signals: list[DocumentFieldSignal] = Field(default_factory=list)
    timeline: list[DocumentTimelineEvent] = Field(default_factory=list)
