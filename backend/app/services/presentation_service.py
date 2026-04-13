from __future__ import annotations

from typing import Any

from app.schemas.application import ApplicationDetail, ApplicationSummary
from app.schemas.common import ApplicationStatus, DocumentStatus
from app.schemas.document import (
    DocumentDetail,
    DocumentFieldSignal,
    DocumentPageMetadata,
    DocumentSummary,
    DocumentTimelineEvent,
    OCRLineRead,
)
from app.schemas.extraction import ExtractionRead
from app.schemas.review import ReviewActionRead
from app.schemas.validation import ValidationFlagRead


def document_requires_attention(document) -> bool:
    return (
        document.status in {
            DocumentStatus.NEEDS_REVIEW.value,
            DocumentStatus.REJECTED.value,
            DocumentStatus.FAILED.value,
        }
        or len(document.validation_flags) > 0
    )


def document_is_review_candidate(document) -> bool:
    return document_requires_attention(document) or document.status == DocumentStatus.PROCESSED.value


def build_document_summary(document) -> DocumentSummary:
    return DocumentSummary(
        id=document.id,
        file_name=document.file_name,
        mime_type=document.mime_type,
        document_type=document.document_type,
        status=DocumentStatus(document.status),
        page_count=len(document.pages),
        validation_flag_count=len(document.validation_flags),
        quality_score=document.quality_score,
        ocr_confidence=document.ocr_confidence,
        extraction_confidence=document.extraction_confidence,
        requires_attention=document_requires_attention(document),
        review_action_count=len(document.review_actions),
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


def build_application_summary(application) -> ApplicationSummary:
    documents = list(application.documents)
    flagged_documents = [document for document in documents if document_requires_attention(document)]
    processed_documents = [
        document
        for document in documents
        if document.status not in {DocumentStatus.UPLOADED.value, DocumentStatus.PROCESSING.value}
    ]
    approved_documents = [
        document for document in documents if document.status == DocumentStatus.APPROVED.value
    ]
    latest_document_updated_at = max(
        (document.updated_at for document in documents),
        default=None,
    )
    review_candidates = sorted(
        (document for document in documents if document_is_review_candidate(document)),
        key=lambda item: item.updated_at,
        reverse=True,
    )
    next_review_document = review_candidates[0] if review_candidates else None

    return ApplicationSummary(
        id=application.id,
        applicant_name=application.applicant_name,
        phone=application.phone,
        email=application.email,
        status=ApplicationStatus(application.status),
        document_count=len(documents),
        processed_document_count=len(processed_documents),
        flagged_document_count=len(flagged_documents),
        approved_document_count=len(approved_documents),
        latest_document_updated_at=latest_document_updated_at,
        next_review_document_id=None if next_review_document is None else next_review_document.id,
        next_review_document_file_name=(
            None if next_review_document is None else next_review_document.file_name
        ),
        next_review_document_updated_at=(
            None if next_review_document is None else next_review_document.updated_at
        ),
        created_at=application.created_at,
        updated_at=application.updated_at,
    )


def build_application_detail(application) -> ApplicationDetail:
    summary = build_application_summary(application)
    return ApplicationDetail(
        **summary.model_dump(),
        documents=[build_document_summary(document) for document in application.documents],
    )


def build_page_metadata(page) -> DocumentPageMetadata:
    ocr_payload = page.ocr_json or {}
    lines = [
        OCRLineRead(
            text=str(line.get("text") or ""),
            bbox=[
                [float(point[0]), float(point[1])]
                for point in line.get("bbox", [])
                if isinstance(point, (list, tuple)) and len(point) >= 2
            ],
            confidence=float(line.get("confidence") or 0.0),
        )
        for line in ocr_payload.get("lines", [])
    ]

    return DocumentPageMetadata(
        id=page.id,
        page_number=page.page_number,
        raw_image_storage_key=page.raw_image_storage_key,
        processed_image_storage_key=page.processed_image_storage_key,
        ocr_text=page.ocr_text,
        ocr_confidence=float(ocr_payload.get("confidence") or 0.0) if ocr_payload else None,
        ocr_lines=lines,
    )


def _normalize_for_match(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")

    return "".join(character.lower() for character in str(value) if character.isalnum())


def _match_ocr_line(value: Any, pages: list[DocumentPageMetadata]):
    normalized_value = _normalize_for_match(value)
    if not normalized_value:
        return None

    best_match = None
    best_score = 0
    for page in pages:
        for line in page.ocr_lines:
            normalized_line = _normalize_for_match(line.text)
            if not normalized_line:
                continue
            if normalized_value in normalized_line:
                score = len(normalized_value)
            elif normalized_line in normalized_value:
                score = len(normalized_line)
            else:
                continue

            if score > best_score:
                best_score = score
                best_match = {
                    "page_number": page.page_number,
                    "bbox": line.bbox,
                    "confidence": line.confidence,
                    "matched_text": line.text,
                }

    return best_match


def build_document_field_signals(document, pages: list[DocumentPageMetadata]) -> list[DocumentFieldSignal]:
    extraction = None if not document.extracted_fields else document.extracted_fields[0].normalized_extraction_json
    if not extraction:
        return []

    flagged_fields = {
        flag.field_name for flag in document.validation_flags if getattr(flag, "field_name", None)
    }
    signals: list[DocumentFieldSignal] = []
    for field_name, value in extraction.items():
        match = _match_ocr_line(value, pages)
        is_missing = value in (None, "")
        signals.append(
            DocumentFieldSignal(
                field_name=field_name,
                value=value,
                page_number=None if match is None else match["page_number"],
                bbox=None if match is None else match["bbox"],
                confidence=(
                    None
                    if is_missing
                    else (
                        document.extraction_confidence
                        if match is None
                        else round(
                            min(
                                0.99,
                                (float(document.extraction_confidence or 0.0) * 0.65)
                                + (float(match["confidence"]) * 0.35),
                            ),
                            4,
                        )
                    )
                ),
                is_flagged=field_name in flagged_fields,
                is_missing=is_missing,
                source="missing" if is_missing else "ocr_line_match" if match else "derived",
                matched_text=None if match is None else match["matched_text"],
            )
        )

    return signals


def build_document_timeline(document, pages: list[DocumentPageMetadata]) -> list[DocumentTimelineEvent]:
    timeline: list[DocumentTimelineEvent] = [
        DocumentTimelineEvent(
            code="upload_received",
            label="Upload received",
            description="Raw file stored and linked to the application.",
            tone="neutral",
            created_at=document.created_at,
        )
    ]

    if pages:
        timeline.append(
            DocumentTimelineEvent(
                code="ocr_completed",
                label="OCR completed",
                description=f"{len(pages)} page(s) generated OCR text and geometry.",
                tone="positive" if any(page.ocr_lines for page in pages) else "pending",
                created_at=max((page.created_at for page in document.pages), default=document.updated_at),
            )
        )

    if document.extracted_fields:
        extraction = document.extracted_fields[0]
        field_count = len(extraction.normalized_extraction_json or {})
        timeline.append(
            DocumentTimelineEvent(
                code="extraction_completed",
                label="AI extraction parsed",
                description=f"{field_count} structured field(s) ready for review.",
                tone="positive",
                created_at=extraction.updated_at,
            )
        )

    timeline.append(
        DocumentTimelineEvent(
            code="validation_completed",
            label="Validation completed",
            description=(
                f"{len(document.validation_flags)} active flag(s) remain."
                if document.validation_flags
                else "No validation flags remain on the current payload."
            ),
            tone="warning" if document.validation_flags else "positive",
            created_at=(
                max((flag.created_at for flag in document.validation_flags), default=None) or document.updated_at
            ),
        )
    )

    for action in document.review_actions:
        timeline.append(
            DocumentTimelineEvent(
                code=f"review_{action.action}",
                label=f"Reviewer {action.action.replace('_', ' ')}",
                description=(
                    f"{action.reviewer_name}"
                    if not action.comment
                    else f"{action.reviewer_name}: {action.comment}"
                ),
                tone=(
                    "positive"
                    if action.action == "approve"
                    else "danger"
                    if action.action == "reject"
                    else "warning"
                ),
                created_at=action.created_at,
            )
        )

    return timeline


def build_document_detail(document) -> DocumentDetail:
    pages = [build_page_metadata(page) for page in document.pages]

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
        pages=pages,
        extraction=(
            None
            if not document.extracted_fields
            else ExtractionRead.model_validate(document.extracted_fields[0])
        ),
        validation_flags=[ValidationFlagRead.model_validate(flag) for flag in document.validation_flags],
        review_actions=[ReviewActionRead.model_validate(action) for action in document.review_actions],
        field_signals=build_document_field_signals(document, pages),
        timeline=build_document_timeline(document, pages),
    )
