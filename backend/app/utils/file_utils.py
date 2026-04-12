from __future__ import annotations

import re
from pathlib import Path

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
SUPPORTED_MIME_TYPES = {
    "image/jpg",
    "image/jpeg",
    "image/png",
    "application/pdf",
}


def sanitize_filename(file_name: str | None) -> str:
    candidate = Path(file_name or "upload").name.strip() or "upload"
    sanitized = re.sub(r"[^A-Za-z0-9._-]", "_", candidate)
    return sanitized[:255]


def is_supported_upload(*, file_name: str, content_type: str) -> bool:
    extension = Path(file_name).suffix.lower()
    return extension in SUPPORTED_EXTENSIONS and content_type in SUPPORTED_MIME_TYPES
