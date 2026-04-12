from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.exceptions import (
    ApplicationNotFoundError,
    DocumentNotFoundError,
    DocumentPageNotFoundError,
    EmptyFileError,
    ProcessingFailureError,
    StorageFailureError,
    UnsupportedFileTypeError,
)
from app.schemas.document import (
    DocumentDetail,
    DocumentPagesResponse,
    DocumentProcessResponse,
    DocumentUploadResponse,
)
from app.schemas.review import (
    ReviewDecisionRequest,
    ReviewDecisionResponse,
    ReviewUpdateRequest,
    ReviewUpdateResponse,
)
from app.services.pipeline_service import PipelineService
from app.services.review_service import ReviewService
from app.services.upload_service import UploadService

router = APIRouter(tags=["documents"])


@router.post(
    "/applications/{application_id}/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    application_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    service = UploadService(db)

    try:
        return await service.upload_document(application_id=application_id, upload_file=file)
    except ApplicationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except EmptyFileError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        ) from exc
    except StorageFailureError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.post(
    "/documents/{document_id}/process",
    response_model=DocumentProcessResponse,
    status_code=status.HTTP_200_OK,
)
async def process_document(
    document_id: str,
    db: Session = Depends(get_db),
) -> DocumentProcessResponse:
    service = PipelineService(db)

    try:
        return service.process_document(document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProcessingFailureError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except StorageFailureError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get(
    "/documents/{document_id}",
    response_model=DocumentDetail,
    status_code=status.HTTP_200_OK,
)
async def get_document_detail(
    document_id: str,
    db: Session = Depends(get_db),
) -> DocumentDetail:
    service = PipelineService(db)

    try:
        return service.get_document_detail(document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get(
    "/documents/{document_id}/pages",
    response_model=DocumentPagesResponse,
    status_code=status.HTTP_200_OK,
)
async def list_document_pages(
    document_id: str,
    db: Session = Depends(get_db),
) -> DocumentPagesResponse:
    service = PipelineService(db)

    try:
        return service.list_document_pages(document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get(
    "/documents/{document_id}/content",
    status_code=status.HTTP_200_OK,
)
async def get_document_content(
    document_id: str,
    db: Session = Depends(get_db),
) -> Response:
    service = PipelineService(db)

    try:
        content, media_type, filename = service.get_document_content(document_id)
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f'inline; filename="{filename}"'},
        )
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except StorageFailureError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get(
    "/documents/{document_id}/pages/{page_number}/content",
    status_code=status.HTTP_200_OK,
)
async def get_document_page_content(
    document_id: str,
    page_number: int,
    variant: str = Query(default="processed"),
    db: Session = Depends(get_db),
) -> Response:
    service = PipelineService(db)

    try:
        content, media_type, filename = service.get_document_page_content(
            document_id=document_id,
            page_number=page_number,
            variant=variant,
        )
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f'inline; filename="{filename}"'},
        )
    except (DocumentNotFoundError, DocumentPageNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProcessingFailureError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except StorageFailureError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.patch(
    "/documents/{document_id}/review",
    response_model=ReviewUpdateResponse,
    status_code=status.HTTP_200_OK,
)
async def update_document_review(
    document_id: str,
    payload: ReviewUpdateRequest,
    db: Session = Depends(get_db),
) -> ReviewUpdateResponse:
    service = ReviewService(db)

    try:
        return service.update_review(document_id, payload)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProcessingFailureError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.post(
    "/documents/{document_id}/decision",
    response_model=ReviewDecisionResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_document_decision(
    document_id: str,
    payload: ReviewDecisionRequest,
    db: Session = Depends(get_db),
) -> ReviewDecisionResponse:
    service = ReviewService(db)

    try:
        return service.submit_decision(document_id, payload)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProcessingFailureError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
