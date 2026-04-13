from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import ApplicationNotFoundError
from app.repositories.application_repository import ApplicationRepository
from app.schemas.application import (
    ApplicationCreateRequest,
    ApplicationDetail,
    ApplicationSummary,
)
from app.schemas.common import ApplicationStatus
from app.services.presentation_service import build_application_detail, build_application_summary


class ApplicationService:
    def __init__(self, db: Session):
        self.repository = ApplicationRepository(db)

    def create_application(self, payload: ApplicationCreateRequest) -> ApplicationSummary:
        application = self.repository.create(
            applicant_name=payload.applicant_name,
            phone=payload.phone,
            email=payload.email,
            status=ApplicationStatus.DRAFT.value,
        )
        return build_application_summary(application)

    def list_applications(self) -> list[ApplicationSummary]:
        applications = self.repository.list()
        return [build_application_summary(application) for application in applications]

    def get_application_detail(self, application_id: str) -> ApplicationDetail:
        application = self.repository.get_by_id(application_id)
        if application is None:
            raise ApplicationNotFoundError(f"Application '{application_id}' was not found.")

        return build_application_detail(application)
