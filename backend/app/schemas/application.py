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
    created_at: datetime
    updated_at: datetime


class ApplicationDetail(ApplicationSummary):
    documents: list[DocumentSummary] = Field(default_factory=list)


class ApplicationListResponse(BaseModel):
    items: list[ApplicationSummary]
