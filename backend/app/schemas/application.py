from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ApplicationStatus, ORMModel
from app.schemas.document import DocumentSummary


class ApplicationCreateRequest(BaseModel):
    applicant_name: str | None = None
    phone: str | None = None
    email: str | None = None


class ApplicationSummary(ORMModel):
    id: str
    applicant_name: str | None = None
    phone: str | None = None
    email: str | None = None
    status: ApplicationStatus
    document_count: int = 0
    processed_document_count: int = 0
    flagged_document_count: int = 0
    approved_document_count: int = 0
    latest_document_updated_at: datetime | None = None
    next_review_document_id: str | None = None
    next_review_document_file_name: str | None = None
    next_review_document_updated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ApplicationDetail(ApplicationSummary):
    documents: list[DocumentSummary] = Field(default_factory=list)


class ApplicationListResponse(BaseModel):
    items: list[ApplicationSummary]
