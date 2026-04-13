from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import httpx

from app.core.config import clear_settings_cache
from app.core.db import clear_db_state, init_db
from app.main import create_app


class UploadFlowTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test.db"
        self.storage_root = Path(self.temp_dir.name) / "storage"

        os.environ["DATABASE_URL"] = f"sqlite:///{self.database_path}"
        os.environ["STORAGE_BACKEND"] = "filesystem"
        os.environ["FILESYSTEM_STORAGE_ROOT"] = str(self.storage_root)
        os.environ["MINIO_BUCKET_NAME"] = "loan-docs"
        os.environ["MAX_REQUEST_SIZE_BYTES"] = str(1024 * 1024)
        os.environ["MAX_UPLOAD_SIZE_BYTES"] = str(512 * 1024)

        clear_settings_cache()
        clear_db_state()
        init_db()

        self.app = create_app()
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=self.app),
            base_url="http://testserver",
        )

    async def asyncTearDown(self) -> None:
        await self.client.aclose()
        clear_db_state()
        clear_settings_cache()

        for variable in (
            "DATABASE_URL",
            "STORAGE_BACKEND",
            "FILESYSTEM_STORAGE_ROOT",
            "MINIO_BUCKET_NAME",
            "MAX_REQUEST_SIZE_BYTES",
            "MAX_UPLOAD_SIZE_BYTES",
        ):
            os.environ.pop(variable, None)

        self.temp_dir.cleanup()

    async def test_create_application(self) -> None:
        response = await self.client.post(
            "/applications",
            json={"applicant_name": "Nguyen Van A", "phone": "0123456789"},
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload["status"], "draft")
        self.assertEqual(payload["applicant_name"], "Nguyen Van A")

    async def test_upload_supported_pdf_persists_raw_object(self) -> None:
        application_id = await self._create_application()

        response = await self.client.post(
            f"/applications/{application_id}/documents",
            files={"file": ("statement.pdf", b"%PDF-1.4 fake payload", "application/pdf")},
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload["upload_status"], "uploaded")

        document_id = payload["document_id"]
        raw_object = (
            self.storage_root
            / "loan-docs"
            / "applications"
            / application_id
            / "raw"
            / document_id
            / "original"
        )
        self.assertTrue(raw_object.exists())

        detail = await self.client.get(f"/applications/{application_id}")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(len(detail.json()["documents"]), 1)
        self.assertEqual(detail.json()["status"], "processing")
        self.assertEqual(detail.json()["document_count"], 1)
        self.assertEqual(detail.json()["processed_document_count"], 0)

        listing = await self.client.get("/applications")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.json()["items"][0]["document_count"], 1)
        self.assertEqual(listing.json()["items"][0]["flagged_document_count"], 0)
        self.assertIsNone(listing.json()["items"][0]["next_review_document_id"])

    async def test_rejects_unsupported_file_type(self) -> None:
        application_id = await self._create_application()

        response = await self.client.post(
            f"/applications/{application_id}/documents",
            files={"file": ("notes.txt", b"hello", "text/plain")},
        )

        self.assertEqual(response.status_code, 415)

    async def test_rejects_empty_file(self) -> None:
        application_id = await self._create_application()

        response = await self.client.post(
            f"/applications/{application_id}/documents",
            files={"file": ("id_card.png", b"", "image/png")},
        )

        self.assertEqual(response.status_code, 400)

    async def test_rejects_oversized_upload(self) -> None:
        application_id = await self._create_application()

        response = await self.client.post(
            f"/applications/{application_id}/documents",
            files={"file": ("big.pdf", b"x" * (600 * 1024), "application/pdf")},
        )

        self.assertEqual(response.status_code, 413)

    async def _create_application(self) -> str:
        response = await self.client.post("/applications", json={"applicant_name": "Tester"})
        self.assertEqual(response.status_code, 201)
        return response.json()["id"]
