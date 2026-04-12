from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.db import check_database_connection
from app.core.exceptions import StorageFailureError
from app.services.storage_service import StorageService

router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
def readiness_check() -> JSONResponse:
    settings = get_settings()
    checks: dict[str, dict[str, str]] = {}
    overall_status = status.HTTP_200_OK

    try:
        check_database_connection()
        checks["database"] = {"status": "ok"}
    except Exception as exc:
        checks["database"] = {"status": "error", "detail": str(exc)}
        overall_status = status.HTTP_503_SERVICE_UNAVAILABLE

    try:
        StorageService(settings).check_connection()
        checks["storage"] = {"status": "ok", "backend": settings.storage_backend}
    except StorageFailureError as exc:
        checks["storage"] = {
            "status": "error",
            "backend": settings.storage_backend,
            "detail": str(exc),
        }
        overall_status = status.HTTP_503_SERVICE_UNAVAILABLE

    checks["ocr"] = {"status": "enabled" if settings.ocr_enabled else "disabled"}
    checks["llm"] = {"status": "enabled" if settings.llm_enabled else "disabled"}

    payload = {
        "status": "ok" if overall_status == status.HTTP_200_OK else "error",
        "checks": checks,
    }
    return JSONResponse(status_code=overall_status, content=payload)
