from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.application import Application
from app.models.document import Document


class ApplicationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        applicant_name: str | None,
        phone: str | None,
        email: str | None,
        status: str,
    ) -> Application:
        application = Application(
            applicant_name=applicant_name,
            phone=phone,
            email=email,
            status=status,
        )
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def list(self) -> list[Application]:
        statement = select(Application).order_by(Application.created_at.desc())
        return list(self.db.scalars(statement))

    def get_by_id(self, application_id: str) -> Application | None:
        statement = (
            select(Application)
            .options(
                selectinload(Application.documents).selectinload(Document.extracted_fields),
                selectinload(Application.documents).selectinload(Document.validation_flags),
                selectinload(Application.documents).selectinload(Document.review_actions),
            )
            .where(Application.id == application_id)
        )
        return self.db.scalar(statement)

    def save(self, application: Application) -> Application:
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application
