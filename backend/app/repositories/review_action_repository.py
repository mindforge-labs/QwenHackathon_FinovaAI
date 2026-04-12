from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.review_action import ReviewAction


class ReviewActionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        document_id: str,
        reviewer_name: str,
        action: str,
        comment: str | None,
        corrected_json: dict | None,
    ) -> ReviewAction:
        record = ReviewAction(
            document_id=document_id,
            reviewer_name=reviewer_name,
            action=action,
            comment=comment,
            corrected_json=corrected_json,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_by_document_id(self, document_id: str) -> list[ReviewAction]:
        statement = (
            select(ReviewAction)
            .where(ReviewAction.document_id == document_id)
            .order_by(ReviewAction.created_at.asc())
        )
        return list(self.db.scalars(statement))
