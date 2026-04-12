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
        return ApplicationSummary.model_validate(application)

    def list_applications(self) -> list[ApplicationSummary]:
        applications = self.repository.list()
        return [ApplicationSummary.model_validate(application) for application in applications]

    def get_application_detail(self, application_id: str) -> ApplicationDetail:
        application = self.repository.get_by_id(application_id)
        if application is None:
            raise ApplicationNotFoundError(f"Application '{application_id}' was not found.")

        return ApplicationDetail.model_validate(application)
