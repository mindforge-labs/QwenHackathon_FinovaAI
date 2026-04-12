from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.validation_flag import ValidationFlag


class ValidationFlagRepository:
    def __init__(self, db: Session):
        self.db = db

    def replace_for_document(self, *, document_id: str, flags: list[dict]) -> list[ValidationFlag]:
        self.db.execute(delete(ValidationFlag).where(ValidationFlag.document_id == document_id))

        created_flags: list[ValidationFlag] = []
        for flag in flags:
            record = ValidationFlag(document_id=document_id, **flag)
            self.db.add(record)
            created_flags.append(record)

        self.db.commit()

        for record in created_flags:
            self.db.refresh(record)

        return created_flags

    def list_by_document_id(self, document_id: str) -> list[ValidationFlag]:
        statement = (
            select(ValidationFlag)
            .where(ValidationFlag.document_id == document_id)
            .order_by(ValidationFlag.created_at.asc())
        )
        return list(self.db.scalars(statement))
