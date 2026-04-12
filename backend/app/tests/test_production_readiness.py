from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import httpx

from app.core.config import clear_settings_cache
from app.core.db import clear_db_state, init_db
from app.core.exceptions import ConfigurationError
from app.main import create_app


class ProductionReadinessTests(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self) -> None:
        clear_db_state()
        clear_settings_cache()
        for variable in (
            "APP_ENV",
            "DEBUG",
            "AUTO_INIT_DB",
            "DATABASE_URL",
            "STORAGE_BACKEND",
            "FILESYSTEM_STORAGE_ROOT",
            "MINIO_BUCKET_NAME",
            "AUTH_ENABLED",
            "API_KEY",
            "OCR_ENABLED",
            "LLM_ENABLED",
            "MAX_REQUEST_SIZE_BYTES",
            "MAX_UPLOAD_SIZE_BYTES",
        ):
            os.environ.pop(variable, None)

    async def test_health_ready_reports_database_and_storage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "test.db"
            storage_root = Path(temp_dir) / "storage"

            os.environ["DATABASE_URL"] = f"sqlite:///{database_path}"
            os.environ["STORAGE_BACKEND"] = "filesystem"
            os.environ["FILESYSTEM_STORAGE_ROOT"] = str(storage_root)
            os.environ["MINIO_BUCKET_NAME"] = "loan-docs"

            clear_settings_cache()
            clear_db_state()
            init_db()

            app = create_app()
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="http://testserver",
            ) as client:
                response = await client.get("/health/ready")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["checks"]["database"]["status"], "ok")
        self.assertEqual(payload["checks"]["storage"]["status"], "ok")
        self.assertEqual(payload["checks"]["storage"]["backend"], "filesystem")

    async def test_applications_endpoint_requires_api_key_when_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "test.db"
            storage_root = Path(temp_dir) / "storage"

            os.environ["DATABASE_URL"] = f"sqlite:///{database_path}"
            os.environ["STORAGE_BACKEND"] = "filesystem"
            os.environ["FILESYSTEM_STORAGE_ROOT"] = str(storage_root)
            os.environ["MINIO_BUCKET_NAME"] = "loan-docs"
            os.environ["AUTH_ENABLED"] = "true"
            os.environ["API_KEY"] = "super-secret"

            clear_settings_cache()
            clear_db_state()
            init_db()

            app = create_app()
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="http://testserver",
            ) as client:
                unauthorized = await client.post(
                    "/applications",
                    json={"applicant_name": "Protected"},
                )
                authorized = await client.post(
                    "/applications",
                    json={"applicant_name": "Protected"},
                    headers={"X-API-Key": "super-secret"},
                )

        self.assertEqual(unauthorized.status_code, 401)
        self.assertEqual(authorized.status_code, 201)

    async def test_production_config_rejects_unsafe_defaults(self) -> None:
        os.environ["APP_ENV"] = "production"
        os.environ["DATABASE_URL"] = "sqlite:///./finova.db"
        os.environ["STORAGE_BACKEND"] = "filesystem"
        os.environ["AUTH_ENABLED"] = "false"
        os.environ["AUTO_INIT_DB"] = "true"

        clear_settings_cache()
        with self.assertRaises(ConfigurationError):
            create_app()

    async def test_invalid_size_limit_config_is_rejected(self) -> None:
        os.environ["MAX_REQUEST_SIZE_BYTES"] = "1024"
        os.environ["MAX_UPLOAD_SIZE_BYTES"] = "2048"

        clear_settings_cache()
        with self.assertRaises(ConfigurationError):
            create_app()
