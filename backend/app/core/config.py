from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

TRUE_VALUES = {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str
    debug: bool
    database_url: str
    storage_backend: str
    filesystem_storage_root: str
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket_name: str
    minio_secure: bool
    ocr_enabled: bool
    ocr_language: str
    ocr_use_angle_cls: bool
    llm_enabled: bool
    llm_base_url: str
    llm_api_key: str
    llm_model: str
    llm_timeout_seconds: float
    cors_origins: tuple[str, ...]

    @property
    def minio_url(self) -> str:
        scheme = "https" if self.minio_secure else "http"
        return f"{scheme}://{self.minio_endpoint}"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Finova AI Backend"),
        debug=os.getenv("DEBUG", "false").lower() in TRUE_VALUES,
        database_url=os.getenv("DATABASE_URL", "sqlite:///./finova.db"),
        storage_backend=os.getenv("STORAGE_BACKEND", "filesystem"),
        filesystem_storage_root=os.getenv("FILESYSTEM_STORAGE_ROOT", "./storage"),
        minio_endpoint=os.getenv("MINIO_ENDPOINT", "minio:9000"),
        minio_access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        minio_secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        minio_bucket_name=os.getenv("MINIO_BUCKET_NAME", "loan-docs"),
        minio_secure=os.getenv("MINIO_SECURE", "false").lower() in TRUE_VALUES,
        ocr_enabled=os.getenv("OCR_ENABLED", "false").lower() in TRUE_VALUES,
        ocr_language=os.getenv("OCR_LANGUAGE", "en"),
        ocr_use_angle_cls=os.getenv("OCR_USE_ANGLE_CLS", "true").lower() in TRUE_VALUES,
        llm_enabled=os.getenv("LLM_ENABLED", "false").lower() in TRUE_VALUES,
        llm_base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        llm_api_key=os.getenv("LLM_API_KEY", ""),
        llm_model=os.getenv("LLM_MODEL", ""),
        llm_timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "30")),
        cors_origins=tuple(
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:3000,http://127.0.0.1:3000",
            ).split(",")
            if origin.strip()
        ),
    )


def clear_settings_cache() -> None:
    get_settings.cache_clear()
