from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from app.core.exceptions import ConfigurationError

TRUE_VALUES = {"1", "true", "yes", "on"}
PRODUCTION_VALUES = {"prod", "production"}


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str
    app_env: str
    debug: bool
    auto_init_db: bool
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
    auth_enabled: bool
    api_key: str
    log_level: str
    log_json: bool
    max_request_size_bytes: int
    max_upload_size_bytes: int

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() in PRODUCTION_VALUES

    @property
    def minio_url(self) -> str:
        scheme = "https" if self.minio_secure else "http"
        return f"{scheme}://{self.minio_endpoint}"


@lru_cache
def get_settings() -> Settings:
    settings = Settings(
        app_name=os.getenv("APP_NAME", "Finova AI Backend"),
        app_env=os.getenv("APP_ENV", "development"),
        debug=os.getenv("DEBUG", "false").lower() in TRUE_VALUES,
        auto_init_db=os.getenv("AUTO_INIT_DB", "true").lower() in TRUE_VALUES,
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
        auth_enabled=os.getenv("AUTH_ENABLED", "false").lower() in TRUE_VALUES,
        api_key=os.getenv("API_KEY", ""),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_json=os.getenv("LOG_JSON", "true").lower() in TRUE_VALUES,
        max_request_size_bytes=int(os.getenv("MAX_REQUEST_SIZE_BYTES", str(10 * 1024 * 1024))),
        max_upload_size_bytes=int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(8 * 1024 * 1024))),
    )
    validate_settings(settings)
    return settings


def validate_settings(settings: Settings) -> None:
    if settings.auth_enabled and not settings.api_key.strip():
        raise ConfigurationError("AUTH_ENABLED is true but API_KEY is empty.")
    if settings.max_request_size_bytes <= 0:
        raise ConfigurationError("MAX_REQUEST_SIZE_BYTES must be greater than zero.")
    if settings.max_upload_size_bytes <= 0:
        raise ConfigurationError("MAX_UPLOAD_SIZE_BYTES must be greater than zero.")
    if settings.max_upload_size_bytes > settings.max_request_size_bytes:
        raise ConfigurationError(
            "MAX_UPLOAD_SIZE_BYTES cannot be greater than MAX_REQUEST_SIZE_BYTES."
        )

    if settings.llm_enabled and not settings.llm_model.strip():
        raise ConfigurationError("LLM_ENABLED is true but LLM_MODEL is empty.")

    if settings.llm_enabled and not settings.llm_base_url.strip():
        raise ConfigurationError("LLM_ENABLED is true but LLM_BASE_URL is empty.")

    if not settings.is_production:
        return

    if settings.debug:
        raise ConfigurationError("Production configuration cannot enable DEBUG.")
    if settings.auto_init_db:
        raise ConfigurationError("Production configuration must disable AUTO_INIT_DB.")
    if settings.database_url == "sqlite:///./finova.db":
        raise ConfigurationError("Production configuration cannot use the default SQLite database.")
    if settings.storage_backend != "minio":
        raise ConfigurationError("Production configuration must use STORAGE_BACKEND=minio.")
    if not settings.auth_enabled:
        raise ConfigurationError("Production configuration must enable API key authentication.")
    if settings.minio_access_key == "minioadmin" or settings.minio_secret_key == "minioadmin":
        raise ConfigurationError("Production configuration cannot use default MinIO credentials.")


def clear_settings_cache() -> None:
    get_settings.cache_clear()
