from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import (
    DocumentNotFoundError,
    DocumentPageNotFoundError,
    ProcessingFailureError,
)
from app.repositories.document_page_repository import DocumentPageRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.extracted_field_repository import ExtractedFieldRepository
from app.repositories.application_repository import ApplicationRepository
from app.repositories.validation_flag_repository import ValidationFlagRepository
from app.schemas.common import DocumentStatus
from app.schemas.document import (
    DocumentDetail,
    DocumentPageMetadata,
    DocumentPagesResponse,
    DocumentProcessResponse,
)
from app.schemas.extraction import ExtractionRead
from app.schemas.review import ReviewActionRead
from app.schemas.validation import ValidationFlagRead
from app.services.classification_service import ClassificationService
from app.services.extraction_service import ExtractionResult, ExtractionService
from app.services.ocr_service import OCRService, build_ocr_service
from app.services.pdf_service import PDFService
from app.services.preprocess_service import PreprocessService
from app.services.storage_service import StorageService
from app.services.validation_service import ValidationService


class PipelineService:
    def __init__(
        self,
        db: Session,
        *,
        storage_service: StorageService | None = None,
        pdf_service: PDFService | None = None,
        preprocess_service: PreprocessService | None = None,
        ocr_service: OCRService | None = None,
        extraction_service: ExtractionService | None = None,
    ):
        self.db = db
        self.document_repository = DocumentRepository(db)
        self.document_page_repository = DocumentPageRepository(db)
        self.extracted_field_repository = ExtractedFieldRepository(db)
        self.validation_flag_repository = ValidationFlagRepository(db)
        self.application_repository = ApplicationRepository(db)
        self.storage_service = storage_service or StorageService()
        self.pdf_service = pdf_service or PDFService()
        self.preprocess_service = preprocess_service or PreprocessService()
        self.ocr_service = ocr_service or build_ocr_service()
        self.classification_service = ClassificationService()
        self.extraction_service = extraction_service or ExtractionService()
        self.validation_service = ValidationService()

    def process_document(self, document_id: str) -> DocumentProcessResponse:
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Document '{document_id}' was not found.")

        self.document_repository.update_status(document, status=DocumentStatus.PROCESSING.value)

        try:
            raw_file = self.storage_service.read_bytes(document.storage_key)
            raw_pages = self._normalize_to_pages(document.mime_type, raw_file)

            page_records: list[dict] = []
            ocr_artifact_pages: list[dict] = []
            for page_number, raw_page_bytes in enumerate(raw_pages, start=1):
                raw_page_key = self.storage_service.build_page_storage_key(
                    application_id=document.application_id,
                    document_id=document.id,
                    page_number=page_number,
                )
                processed_page_key = self.storage_service.build_processed_page_storage_key(
                    application_id=document.application_id,
                    document_id=document.id,
                    page_number=page_number,
                )

                processed_page_bytes = self.preprocess_service.preprocess_for_ocr(raw_page_bytes)
                ocr_result = self.ocr_service.run_page(
                    image_bytes=processed_page_bytes,
                    page_number=page_number,
                )
                self.storage_service.store_bytes(
                    storage_key=raw_page_key,
                    content_type="image/jpeg",
                    data=raw_page_bytes,
                )
                self.storage_service.store_bytes(
                    storage_key=processed_page_key,
                    content_type="image/jpeg",
                    data=processed_page_bytes,
                )

                page_records.append(
                    {
                        "page_number": page_number,
                        "raw_image_storage_key": raw_page_key,
                        "processed_image_storage_key": processed_page_key,
                        "ocr_text": ocr_result.text or None,
                        "ocr_json": ocr_result.as_json(),
                    }
                )
                ocr_artifact_pages.append(ocr_result.as_json())

            self.document_page_repository.replace_for_document(
                document_id=document.id,
                pages=page_records,
            )
            aggregated_ocr_text = "\n".join(page.get("text", "") for page in ocr_artifact_pages).strip()
            classification = self.classification_service.classify(aggregated_ocr_text)
            document.ocr_confidence = self._aggregate_document_ocr_confidence(ocr_artifact_pages)
            document.document_type = classification.document_type
            extraction_result: ExtractionResult | None = None
            raw_extraction: dict | None = None
            normalized_extraction: dict | None = None
            extraction_confidence: float | None = None

            self.extracted_field_repository.delete_for_document(document.id)
            if classification.document_type != "unknown" and aggregated_ocr_text:
                extraction_result = self.extraction_service.extract(
                    document_type=classification.document_type,
                    ocr_text=aggregated_ocr_text,
                )
                raw_extraction = extraction_result.raw
                normalized_extraction = extraction_result.normalized
                self.extracted_field_repository.replace_for_document(
                    document_id=document.id,
                    schema_version="1.0",
                    raw_extraction_json=raw_extraction,
                    normalized_extraction_json=normalized_extraction,
                )
                extraction_confidence = self.validation_service.compute_extraction_confidence(
                    document_type=classification.document_type,
                    normalized_extraction=normalized_extraction,
                    classification_confidence=classification.confidence,
                    ocr_confidence=document.ocr_confidence,
                    extraction_source=extraction_result.source,
                    llm_attempt_count=extraction_result.llm_attempt_count,
                    fallback_used=extraction_result.fallback_used,
                )
                self._store_extraction_artifact(
                    application_id=document.application_id,
                    document_id=document.id,
                    raw_extraction=raw_extraction,
                    normalized_extraction=normalized_extraction,
                    extraction_confidence=extraction_confidence,
                    extraction_source=extraction_result.source,
                    llm_attempt_count=extraction_result.llm_attempt_count,
                    fallback_used=extraction_result.fallback_used,
                )

            document.extraction_confidence = extraction_confidence
            flags = self.validation_service.build_processing_flags(
                document_type=classification.document_type,
                classification_confidence=classification.confidence,
                ocr_text=aggregated_ocr_text,
                ocr_confidence=document.ocr_confidence,
            )
            flags.extend(
                self.validation_service.build_extraction_flags(
                    document_type=classification.document_type,
                    normalized_extraction=normalized_extraction,
                    extraction_confidence=extraction_confidence,
                    extraction_source=None if extraction_result is None else extraction_result.source,
                    llm_attempt_count=0 if extraction_result is None else extraction_result.llm_attempt_count,
                    fallback_used=False if extraction_result is None else extraction_result.fallback_used,
                )
            )
            document.status = self._resolve_document_status(
                document_type=classification.document_type,
                ocr_text=aggregated_ocr_text,
                ocr_confidence=document.ocr_confidence,
                extraction_confidence=extraction_confidence,
                flags=flags,
            )
            document = self.document_repository.save(document)
            self.validation_flag_repository.replace_for_document(
                document_id=document.id,
                flags=flags,
            )
            self._refresh_cross_document_validation(document.application_id)
            self._store_ocr_artifact(
                application_id=document.application_id,
                document_id=document.id,
                pages=ocr_artifact_pages,
                ocr_confidence=document.ocr_confidence,
            )
        except ProcessingFailureError:
            self.db.rollback()
            self.document_repository.update_status_by_id(
                document_id,
                status=DocumentStatus.FAILED.value,
            )
            raise
        except Exception as exc:
            self.db.rollback()
            self.document_repository.update_status_by_id(
                document_id,
                status=DocumentStatus.FAILED.value,
            )
            raise ProcessingFailureError("Document processing failed unexpectedly.") from exc

        return DocumentProcessResponse(
            document_id=document.id,
            processing_status=DocumentStatus(document.status),
            page_count=len(page_records),
        )

    def list_document_pages(self, document_id: str) -> DocumentPagesResponse:
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Document '{document_id}' was not found.")

        pages = self.document_page_repository.list_by_document_id(document_id)
        return DocumentPagesResponse(
            document_id=document_id,
            items=[DocumentPageMetadata.model_validate(page) for page in pages],
        )

    def get_document_detail(self, document_id: str) -> DocumentDetail:
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Document '{document_id}' was not found.")

        return DocumentDetail(
            id=document.id,
            application_id=document.application_id,
            file_name=document.file_name,
            mime_type=document.mime_type,
            storage_key=document.storage_key,
            document_type=document.document_type,
            status=DocumentStatus(document.status),
            page_count=len(document.pages),
            quality_score=document.quality_score,
            ocr_confidence=document.ocr_confidence,
            extraction_confidence=document.extraction_confidence,
            created_at=document.created_at,
            updated_at=document.updated_at,
            pages=[DocumentPageMetadata.model_validate(page) for page in document.pages],
            extraction=(
                None
                if not document.extracted_fields
                else ExtractionRead.model_validate(document.extracted_fields[0])
            ),
            validation_flags=[
                ValidationFlagRead.model_validate(flag) for flag in document.validation_flags
            ],
            review_actions=[ReviewActionRead.model_validate(action) for action in document.review_actions],
        )

    def get_document_content(self, document_id: str) -> tuple[bytes, str, str]:
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Document '{document_id}' was not found.")

        return (
            self.storage_service.read_bytes(document.storage_key),
            document.mime_type,
            document.file_name,
        )

    def get_document_page_content(
        self,
        *,
        document_id: str,
        page_number: int,
        variant: str,
    ) -> tuple[bytes, str, str]:
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Document '{document_id}' was not found.")

        page = self.document_page_repository.get_by_document_id_and_page_number(
            document_id=document_id,
            page_number=page_number,
        )
        if page is None:
            raise DocumentPageNotFoundError(
                f"Page '{page_number}' for document '{document_id}' was not found."
            )

        if variant == "raw":
            storage_key = page.raw_image_storage_key
        elif variant == "processed":
            storage_key = page.processed_image_storage_key
        else:
            raise ProcessingFailureError(f"Unsupported page content variant '{variant}'.")

        return (
            self.storage_service.read_bytes(storage_key),
            "image/jpeg",
            f"{document_id}-{page_number}-{variant}.jpg",
        )

    def _normalize_to_pages(self, mime_type: str, raw_file: bytes) -> list[bytes]:
        if mime_type == "application/pdf":
            return self.pdf_service.render_pdf_to_jpeg_pages(raw_file)

        return [self.preprocess_service.normalize_image_to_jpeg(raw_file)]

    def _aggregate_document_ocr_confidence(self, pages: list[dict]) -> float:
        if not pages:
            return 0.0

        weighted_score = 0.0
        total_weight = 0
        for page in pages:
            text = str(page.get("text") or "")
            confidence = float(page.get("confidence") or 0.0)
            weight = max(len(text.replace("\n", "").strip()), 1)
            weighted_score += confidence * weight
            total_weight += weight

        return weighted_score / total_weight if total_weight else 0.0

    def _store_ocr_artifact(
        self,
        *,
        application_id: str,
        document_id: str,
        pages: list[dict],
        ocr_confidence: float | None,
    ) -> None:
        artifact_key = self.storage_service.build_ocr_artifact_storage_key(
            application_id=application_id,
            document_id=document_id,
        )
        payload = {
            "document_id": document_id,
            "ocr_confidence": ocr_confidence,
            "pages": pages,
        }
        import json

        self.storage_service.store_bytes(
            storage_key=artifact_key,
            content_type="application/json",
            data=json.dumps(payload).encode("utf-8"),
        )

    def _store_extraction_artifact(
        self,
        *,
        application_id: str,
        document_id: str,
        raw_extraction: dict | None,
        normalized_extraction: dict | None,
        extraction_confidence: float | None,
        extraction_source: str,
        llm_attempt_count: int,
        fallback_used: bool,
    ) -> None:
        artifact_key = self.storage_service.build_extraction_artifact_storage_key(
            application_id=application_id,
            document_id=document_id,
        )
        payload = {
            "document_id": document_id,
            "extraction_confidence": extraction_confidence,
            "extraction_source": extraction_source,
            "llm_attempt_count": llm_attempt_count,
            "fallback_used": fallback_used,
            "raw_extraction_json": raw_extraction,
            "normalized_extraction_json": normalized_extraction,
        }
        import json

        self.storage_service.store_bytes(
            storage_key=artifact_key,
            content_type="application/json",
            data=json.dumps(payload).encode("utf-8"),
        )

    def _resolve_document_status(
        self,
        *,
        document_type: str,
        ocr_text: str,
        ocr_confidence: float | None,
        extraction_confidence: float | None,
        flags: list[dict],
    ) -> str:
        if not ocr_text.strip():
            return DocumentStatus.NEEDS_REVIEW.value
        if document_type == "unknown":
            return DocumentStatus.NEEDS_REVIEW.value
        if ocr_confidence is not None and ocr_confidence < 0.5:
            return DocumentStatus.NEEDS_REVIEW.value
        if extraction_confidence is not None and extraction_confidence < 0.6:
            return DocumentStatus.NEEDS_REVIEW.value
        if any(flag["severity"] == "error" for flag in flags):
            return DocumentStatus.NEEDS_REVIEW.value
        return DocumentStatus.PROCESSED.value

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

            if cross_flags.get(document.id) and document.status == DocumentStatus.PROCESSED.value:
                document.status = DocumentStatus.NEEDS_REVIEW.value
                self.document_repository.save(document)
