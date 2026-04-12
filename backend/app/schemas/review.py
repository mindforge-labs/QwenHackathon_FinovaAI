from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import DocumentStatus, ORMModel
from app.schemas.extraction import ExtractionRead


ReviewDecisionAction = Literal["approve", "reject", "request_reupload"]


class ReviewActionRead(ORMModel):
    id: str
    reviewer_name: str
    action: str
    comment: str | None = None
    corrected_json: dict | None = None
    created_at: datetime


class ReviewUpdateRequest(BaseModel):
    reviewer_name: str = Field(min_length=1)
    corrected_json: dict
    comment: str | None = None


class ReviewDecisionRequest(BaseModel):
    reviewer_name: str = Field(min_length=1)
    action: ReviewDecisionAction
    comment: str | None = None


class ReviewUpdateResponse(ORMModel):
    document_id: str
    status: DocumentStatus
    extraction: ExtractionRead
    review_action: ReviewActionRead


class ReviewDecisionResponse(ORMModel):
    document_id: str
    status: DocumentStatus
    review_action: ReviewActionRead
