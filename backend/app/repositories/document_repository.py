from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.document import Document


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        document_id: str,
        application_id: str,
        file_name: str,
        mime_type: str,
        storage_key: str,
        status: str,
    ) -> Document:
        document = Document(
            id=document_id,
            application_id=application_id,
            file_name=file_name,
            mime_type=mime_type,
            storage_key=storage_key,
            status=status,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_by_id(self, document_id: str) -> Document | None:
        statement = (
            select(Document)
            .options(
                selectinload(Document.pages),
                selectinload(Document.extracted_fields),
                selectinload(Document.review_actions),
                selectinload(Document.validation_flags),
            )
            .where(Document.id == document_id)
        )
        return self.db.scalar(statement)

    def update_status(self, document: Document, *, status: str) -> Document:
        document.status = status
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def save(self, document: Document) -> Document:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
