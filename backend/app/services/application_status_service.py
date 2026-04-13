from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.application_repository import ApplicationRepository
from app.schemas.common import ApplicationStatus, DocumentStatus


class ApplicationStatusService:
    def __init__(self, db: Session):
        self.application_repository = ApplicationRepository(db)

    def sync(self, application_id: str):
        application = self.application_repository.get_by_id(application_id)
        if application is None:
            return None

        document_statuses = {document.status for document in application.documents}
        if not document_statuses:
            application.status = ApplicationStatus.DRAFT.value
        elif all(status == DocumentStatus.APPROVED.value for status in document_statuses):
            application.status = ApplicationStatus.APPROVED.value
        elif any(status == DocumentStatus.REJECTED.value for status in document_statuses):
            application.status = ApplicationStatus.REJECTED.value
        elif any(
            status in {
                DocumentStatus.NEEDS_REVIEW.value,
                DocumentStatus.PROCESSED.value,
                DocumentStatus.APPROVED.value,
                DocumentStatus.FAILED.value,
            }
            for status in document_statuses
        ):
            application.status = ApplicationStatus.UNDER_REVIEW.value
        else:
            application.status = ApplicationStatus.PROCESSING.value

        return self.application_repository.save(application)
