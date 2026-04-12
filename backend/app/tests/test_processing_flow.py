from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import cv2
import fitz
import httpx
import numpy as np

from app.core.config import clear_settings_cache
from app.core.db import clear_db_state, init_db
from app.main import create_app


class ProcessingFlowTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test.db"
        self.storage_root = Path(self.temp_dir.name) / "storage"

        os.environ["DATABASE_URL"] = f"sqlite:///{self.database_path}"
        os.environ["STORAGE_BACKEND"] = "filesystem"
        os.environ["FILESYSTEM_STORAGE_ROOT"] = str(self.storage_root)
        os.environ["MINIO_BUCKET_NAME"] = "loan-docs"

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
        ):
            os.environ.pop(variable, None)

        self.temp_dir.cleanup()

    async def test_process_uploaded_png_creates_page_artifacts(self) -> None:
        application_id = await self._create_application()
        image_bytes = self._create_png_bytes()
        upload = await self.client.post(
            f"/applications/{application_id}/documents",
            files={"file": ("card.png", image_bytes, "image/png")},
        )
        document_id = upload.json()["document_id"]

        process = await self.client.post(f"/documents/{document_id}/process")

        self.assertEqual(process.status_code, 200)
        self.assertEqual(process.json()["processing_status"], "needs_review")
        self.assertEqual(process.json()["page_count"], 1)

        pages = await self.client.get(f"/documents/{document_id}/pages")
        self.assertEqual(pages.status_code, 200)
        self.assertEqual(len(pages.json()["items"]), 1)

        raw_page = (
            self.storage_root
            / "loan-docs"
            / "applications"
            / application_id
            / "pages"
            / document_id
            / "1.jpg"
        )
        processed_page = (
            self.storage_root
            / "loan-docs"
            / "applications"
            / application_id
            / "processed"
            / document_id
            / "1.jpg"
        )
        self.assertTrue(raw_page.exists())
        self.assertTrue(processed_page.exists())

        processed_preview = await self.client.get(
            f"/documents/{document_id}/pages/1/content",
            params={"variant": "processed"},
        )
        self.assertEqual(processed_preview.status_code, 200)
        self.assertEqual(processed_preview.headers["content-type"], "image/jpeg")

    async def test_process_uploaded_pdf_creates_multiple_pages(self) -> None:
        application_id = await self._create_application()
        pdf_bytes = self._create_pdf_bytes(page_count=2)
        upload = await self.client.post(
            f"/applications/{application_id}/documents",
            files={"file": ("statement.pdf", pdf_bytes, "application/pdf")},
        )
        document_id = upload.json()["document_id"]

        process = await self.client.post(f"/documents/{document_id}/process")

        self.assertEqual(process.status_code, 200)
        self.assertEqual(process.json()["processing_status"], "needs_review")
        self.assertEqual(process.json()["page_count"], 2)

        pages = await self.client.get(f"/documents/{document_id}/pages")
        self.assertEqual(pages.status_code, 200)
        self.assertEqual(len(pages.json()["items"]), 2)

        original_preview = await self.client.get(f"/documents/{document_id}/content")
        self.assertEqual(original_preview.status_code, 200)
        self.assertEqual(original_preview.headers["content-type"], "application/pdf")

    async def _create_application(self) -> str:
        response = await self.client.post("/applications", json={"applicant_name": "Processor"})
        self.assertEqual(response.status_code, 201)
        return response.json()["id"]

    def _create_png_bytes(self) -> bytes:
        image = np.full((240, 360, 3), 255, dtype=np.uint8)
        cv2.putText(
            image,
            "ID CARD",
            (30, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 0, 0),
            2,
            cv2.LINE_AA,
        )
        ok, encoded = cv2.imencode(".png", image)
        if not ok:
            raise AssertionError("Could not create PNG fixture.")
        return encoded.tobytes()

    def _create_pdf_bytes(self, *, page_count: int) -> bytes:
        document = fitz.open()
        try:
            for page_number in range(page_count):
                page = document.new_page()
                page.insert_text((72, 72), f"Statement Page {page_number + 1}", fontsize=18)
            return document.tobytes()
        finally:
            document.close()
