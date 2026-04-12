from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.document_page import DocumentPage


class DocumentPageRepository:
    def __init__(self, db: Session):
        self.db = db

    def replace_for_document(self, *, document_id: str, pages: list[dict]) -> list[DocumentPage]:
        self.db.execute(delete(DocumentPage).where(DocumentPage.document_id == document_id))

        created_pages: list[DocumentPage] = []
        for page in pages:
            record = DocumentPage(document_id=document_id, **page)
            self.db.add(record)
            created_pages.append(record)

        self.db.commit()

        for record in created_pages:
            self.db.refresh(record)

        return created_pages

    def list_by_document_id(self, document_id: str) -> list[DocumentPage]:
        statement = (
            select(DocumentPage)
            .where(DocumentPage.document_id == document_id)
            .order_by(DocumentPage.page_number.asc())
        )
        return list(self.db.scalars(statement))

    def list_for_document(self, document_id: str) -> list[DocumentPage]:
        return self.list_by_document_id(document_id)

    def get_by_document_id_and_page_number(
        self,
        *,
        document_id: str,
        page_number: int,
    ) -> DocumentPage | None:
        statement = select(DocumentPage).where(
            DocumentPage.document_id == document_id,
            DocumentPage.page_number == page_number,
        )
        return self.db.scalar(statement)
