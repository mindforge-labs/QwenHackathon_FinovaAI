from __future__ import annotations

from app.core.config import Settings
from app.core.exceptions import StorageFailureError


def build_s3_client(settings: Settings):
    try:
        import boto3
    except ImportError as exc:
        raise StorageFailureError("boto3 is required for MinIO-backed storage.") from exc

    return boto3.client(
        "s3",
        endpoint_url=settings.minio_url,
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        region_name="us-east-1",
    )


def ensure_bucket(client, bucket_name: str) -> None:
    try:
        client.head_bucket(Bucket=bucket_name)
    except Exception:
        client.create_bucket(Bucket=bucket_name)
