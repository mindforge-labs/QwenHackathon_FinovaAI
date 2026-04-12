from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import DocumentNotFoundError, ProcessingFailureError
from app.repositories.application_repository import ApplicationRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.extracted_field_repository import ExtractedFieldRepository
from app.repositories.review_action_repository import ReviewActionRepository
from app.schemas.common import ApplicationStatus, DocumentStatus
from app.schemas.extraction import ExtractionRead
from app.schemas.review import (
    ReviewActionRead,
    ReviewDecisionRequest,
    ReviewDecisionResponse,
    ReviewUpdateRequest,
    ReviewUpdateResponse,
)
from app.services.extraction_service import ExtractionService
from app.services.validation_service import ValidationService


class ReviewService:
    def __init__(self, db: Session):
        self.document_repository = DocumentRepository(db)
        self.extracted_field_repository = ExtractedFieldRepository(db)
        self.review_action_repository = ReviewActionRepository(db)
        self.application_repository = ApplicationRepository(db)
        from app.repositories.validation_flag_repository import ValidationFlagRepository

        self.validation_flag_repository = ValidationFlagRepository(db)
        self.extraction_service = ExtractionService()
        self.validation_service = ValidationService()

    def update_review(
        self,
        document_id: str,
        payload: ReviewUpdateRequest,
    ) -> ReviewUpdateResponse:
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Document '{document_id}' was not found.")
        if document.document_type in (None, "unknown"):
            raise ProcessingFailureError("Cannot review corrected extraction for an unknown document type.")

        normalized = self.extraction_service._validate_and_normalize(  # noqa: SLF001
            document_type=document.document_type,
            payload=payload.corrected_json,
        )
        extraction = self.extracted_field_repository.replace_for_document(
            document_id=document.id,
            schema_version="1.0",
            raw_extraction_json=payload.corrected_json,
            normalized_extraction_json=normalized,
        )
        self.document_repository.db.expire_all()
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Document '{document_id}' was not found.")
        review_action = self.review_action_repository.create(
            document_id=document.id,
            reviewer_name=payload.reviewer_name.strip(),
            action="correct_fields",
            comment=payload.comment,
            corrected_json=normalized,
        )
        document.status = DocumentStatus.NEEDS_REVIEW.value
        document = self.document_repository.save(document)
        self._refresh_cross_document_validation(document.application_id)
        self._sync_application_status(document.application_id)

        return ReviewUpdateResponse(
            document_id=document.id,
            status=DocumentStatus(document.status),
            extraction=ExtractionRead.model_validate(extraction),
            review_action=ReviewActionRead.model_validate(review_action),
        )

    def submit_decision(
        self,
        document_id: str,
        payload: ReviewDecisionRequest,
    ) -> ReviewDecisionResponse:
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Document '{document_id}' was not found.")

        next_status = self._resolve_document_status(payload.action)
        document.status = next_status.value
        document = self.document_repository.save(document)
        review_action = self.review_action_repository.create(
            document_id=document.id,
            reviewer_name=payload.reviewer_name.strip(),
            action=payload.action,
            comment=payload.comment,
            corrected_json=None,
        )
        self._refresh_cross_document_validation(document.application_id)
        self._sync_application_status(document.application_id)

        return ReviewDecisionResponse(
            document_id=document.id,
            status=next_status,
            review_action=ReviewActionRead.model_validate(review_action),
        )

    def _resolve_document_status(self, action: str) -> DocumentStatus:
        if action == "approve":
            return DocumentStatus.APPROVED
        if action == "reject":
            return DocumentStatus.REJECTED
        if action == "request_reupload":
            return DocumentStatus.NEEDS_REVIEW
        raise ProcessingFailureError(f"Unsupported review action '{action}'.")

    def _sync_application_status(self, application_id: str) -> None:
        application = self.application_repository.get_by_id(application_id)
        if application is None:
            return

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
            }
            for status in document_statuses
        ):
            application.status = ApplicationStatus.UNDER_REVIEW.value
        else:
            application.status = ApplicationStatus.PROCESSING.value

        self.application_repository.save(application)

    def _refresh_cross_document_validation(self, application_id: str) -> None:
        self.document_repository.db.expire_all()
        application = self.application_repository.get_by_id(application_id)
        if application is None:
            return

        cross_flags = self.validation_service.build_cross_document_flags(application.documents)

        for document in application.documents:
            base_flags = [
                {
                    "flag_code": flag.flag_code,
                    "severity": flag.severity,
                    "message": flag.message,
                    "field_name": flag.field_name,
                }
                for flag in document.validation_flags
                if flag.flag_code != "NAME_MISMATCH"
            ]
            merged_flags = base_flags + cross_flags.get(document.id, [])
            self.validation_flag_repository.replace_for_document(
                document_id=document.id,
                flags=merged_flags,
            )
