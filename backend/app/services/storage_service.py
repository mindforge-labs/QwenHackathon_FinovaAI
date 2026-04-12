from __future__ import annotations

from pathlib import Path

from app.core.config import Settings, get_settings
from app.core.exceptions import StorageFailureError
from app.core.s3 import build_s3_client, ensure_bucket


class StorageService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def build_raw_storage_key(self, *, application_id: str, document_id: str) -> str:
        return f"applications/{application_id}/raw/{document_id}/original"

    def build_page_storage_key(
        self,
        *,
        application_id: str,
        document_id: str,
        page_number: int,
    ) -> str:
        return f"applications/{application_id}/pages/{document_id}/{page_number}.jpg"

    def build_processed_page_storage_key(
        self,
        *,
        application_id: str,
        document_id: str,
        page_number: int,
    ) -> str:
        return f"applications/{application_id}/processed/{document_id}/{page_number}.jpg"

    def build_ocr_artifact_storage_key(self, *, application_id: str, document_id: str) -> str:
        return f"applications/{application_id}/artifacts/{document_id}/ocr.json"

    def build_extraction_artifact_storage_key(self, *, application_id: str, document_id: str) -> str:
        return f"applications/{application_id}/artifacts/{document_id}/extraction.json"

    def store_raw_file(
        self,
        *,
        application_id: str,
        document_id: str,
        content_type: str,
        data: bytes,
    ) -> str:
        storage_key = self.build_raw_storage_key(
            application_id=application_id,
            document_id=document_id,
        )

        self.store_bytes(storage_key=storage_key, content_type=content_type, data=data)

        return storage_key

    def store_bytes(self, *, storage_key: str, content_type: str, data: bytes) -> None:
        if self.settings.storage_backend == "filesystem":
            self._store_to_filesystem(storage_key=storage_key, data=data)
        elif self.settings.storage_backend == "minio":
            self._store_to_minio(
                storage_key=storage_key,
                content_type=content_type,
                data=data,
            )
        else:
            raise StorageFailureError(
                f"Unsupported storage backend '{self.settings.storage_backend}'."
            )

    def read_bytes(self, storage_key: str) -> bytes:
        if self.settings.storage_backend == "filesystem":
            return self._read_from_filesystem(storage_key)
        if self.settings.storage_backend == "minio":
            return self._read_from_minio(storage_key)

        raise StorageFailureError(f"Unsupported storage backend '{self.settings.storage_backend}'.")

    def _store_to_filesystem(self, *, storage_key: str, data: bytes) -> None:
        target = self._filesystem_target(storage_key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def _read_from_filesystem(self, storage_key: str) -> bytes:
        target = self._filesystem_target(storage_key)
        try:
            return target.read_bytes()
        except FileNotFoundError as exc:
            raise StorageFailureError(f"Stored object '{storage_key}' was not found.") from exc

    def _store_to_minio(self, *, storage_key: str, content_type: str, data: bytes) -> None:
        try:
            client = build_s3_client(self.settings)
            ensure_bucket(client, self.settings.minio_bucket_name)
            client.put_object(
                Bucket=self.settings.minio_bucket_name,
                Key=storage_key,
                Body=data,
                ContentType=content_type,
            )
        except Exception as exc:
            raise StorageFailureError("Could not store the raw upload in MinIO.") from exc

    def _read_from_minio(self, storage_key: str) -> bytes:
        try:
            client = build_s3_client(self.settings)
            response = client.get_object(
                Bucket=self.settings.minio_bucket_name,
                Key=storage_key,
            )
            return response["Body"].read()
        except Exception as exc:
            raise StorageFailureError("Could not read the stored object from MinIO.") from exc

    def _filesystem_target(self, storage_key: str) -> Path:
        root = Path(self.settings.filesystem_storage_root)
        return root / self.settings.minio_bucket_name / storage_key
