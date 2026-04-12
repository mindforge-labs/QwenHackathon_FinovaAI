from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.exceptions import ApplicationNotFoundError
from app.core.security import require_api_key
from app.schemas.application import (
    ApplicationCreateRequest,
    ApplicationDetail,
    ApplicationListResponse,
    ApplicationSummary,
)
from app.services.application_service import ApplicationService

router = APIRouter(
    prefix="/applications",
    tags=["applications"],
    dependencies=[Depends(require_api_key)],
)


@router.post("", response_model=ApplicationSummary, status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreateRequest,
    db: Session = Depends(get_db),
) -> ApplicationSummary:
    service = ApplicationService(db)
    return service.create_application(payload)


@router.get("", response_model=ApplicationListResponse)
async def list_applications(db: Session = Depends(get_db)) -> ApplicationListResponse:
    service = ApplicationService(db)
    return ApplicationListResponse(items=service.list_applications())


@router.get("/{application_id}", response_model=ApplicationDetail)
async def get_application_detail(
    application_id: str,
    db: Session = Depends(get_db),
) -> ApplicationDetail:
    service = ApplicationService(db)

    try:
        return service.get_application_detail(application_id)
    except ApplicationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
