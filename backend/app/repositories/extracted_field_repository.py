from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.extracted_field import ExtractedField


class ExtractedFieldRepository:
    def __init__(self, db: Session):
        self.db = db

    def delete_for_document(self, document_id: str) -> None:
        self.db.execute(delete(ExtractedField).where(ExtractedField.document_id == document_id))
        self.db.commit()

    def replace_for_document(
        self,
        *,
        document_id: str,
        schema_version: str,
        raw_extraction_json: dict,
        normalized_extraction_json: dict,
    ) -> ExtractedField:
        self.db.execute(delete(ExtractedField).where(ExtractedField.document_id == document_id))
        record = ExtractedField(
            document_id=document_id,
            schema_version=schema_version,
            raw_extraction_json=raw_extraction_json,
            normalized_extraction_json=normalized_extraction_json,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_document_id(self, document_id: str) -> ExtractedField | None:
        statement = select(ExtractedField).where(ExtractedField.document_id == document_id)
        return self.db.scalar(statement)
