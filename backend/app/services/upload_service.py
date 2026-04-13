from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ApplicationNotFoundError,
    EmptyFileError,
    RequestTooLargeError,
    UnsupportedFileTypeError,
)
from app.core.config import get_settings
from app.repositories.application_repository import ApplicationRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.common import DocumentStatus
from app.schemas.document import DocumentUploadResponse
from app.services.application_status_service import ApplicationStatusService
from app.services.storage_service import StorageService
from app.utils.file_utils import is_supported_upload, sanitize_filename
from app.utils.hashing_utils import sha256_bytes

logger = logging.getLogger(__name__)


class UploadService:
    def __init__(self, db: Session, storage_service: StorageService | None = None):
        self.application_repository = ApplicationRepository(db)
        self.document_repository = DocumentRepository(db)
        self.application_status_service = ApplicationStatusService(db)
        self.storage_service = storage_service or StorageService()
        self.settings = get_settings()

    async def upload_document(
        self,
        *,
        application_id: str,
        upload_file: UploadFile,
    ) -> DocumentUploadResponse:
        application = self.application_repository.get_by_id(application_id)
        if application is None:
            raise ApplicationNotFoundError(f"Application '{application_id}' was not found.")

        safe_file_name = sanitize_filename(upload_file.filename)
        content_type = upload_file.content_type or "application/octet-stream"

        if not is_supported_upload(file_name=safe_file_name, content_type=content_type):
            raise UnsupportedFileTypeError(
                f"Unsupported upload '{safe_file_name}' with MIME type '{content_type}'."
            )

        content = await upload_file.read()
        if not content:
            raise EmptyFileError("Uploaded file is empty.")
        if len(content) > self.settings.max_upload_size_bytes:
            raise RequestTooLargeError("Uploaded file exceeds the configured size limit.")

        # Keep the hash available for duplicate-detection work later.
        _file_hash = sha256_bytes(content)

        document_id = str(uuid4())
        storage_key = self.storage_service.store_raw_file(
            application_id=application_id,
            document_id=document_id,
            content_type=content_type,
            data=content,
        )

        document = self.document_repository.create(
            document_id=document_id,
            application_id=application_id,
            file_name=safe_file_name,
            mime_type=content_type,
            storage_key=storage_key,
            status=DocumentStatus.UPLOADED.value,
        )
        self.application_status_service.sync(application_id)

        logger.info(
            "document upload stored",
            extra={
                "event": "document_upload_stored",
                "application_id": application_id,
                "document_id": document.id,
                "file_name": safe_file_name,
                "mime_type": content_type,
                "storage_key": storage_key,
            },
        )

        return DocumentUploadResponse(
            document_id=document.id,
            upload_status=DocumentStatus(document.status),
        )
