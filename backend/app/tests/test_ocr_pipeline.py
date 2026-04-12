from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import cv2
import httpx
import numpy as np

from app.core.config import clear_settings_cache
from app.core.db import clear_db_state, get_session_factory, init_db
from app.repositories.document_page_repository import DocumentPageRepository
from app.repositories.document_repository import DocumentRepository
from app.services.ocr_service import OCRLine, OCRPageResult, OCRService
from app.services.pipeline_service import PipelineService
from app.services.storage_service import StorageService
from app.main import create_app


class FakeOCRService(OCRService):
    def run_page(self, *, image_bytes: bytes, page_number: int) -> OCRPageResult:
        text = (
            "Employee Name: Jane Doe\n"
            "Employer: Finova AI\n"
            "Pay Period: 03/2026\n"
            "Gross Salary: 1500\n"
            "Net Salary: 1200\n"
            "salary net salary gross salary pay period"
        )
        line = OCRLine(
            text=text,
            bbox=[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]],
            confidence=0.87,
        )
        return OCRPageResult(
            page_number=page_number,
            text=text,
            lines=[line],
            confidence=0.87,
        )


class OCRPipelineTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test.db"
        self.storage_root = Path(self.temp_dir.name) / "storage"

        os.environ["DATABASE_URL"] = f"sqlite:///{self.database_path}"
        os.environ["STORAGE_BACKEND"] = "filesystem"
        os.environ["FILESYSTEM_STORAGE_ROOT"] = str(self.storage_root)
        os.environ["MINIO_BUCKET_NAME"] = "loan-docs"
        os.environ["OCR_ENABLED"] = "false"

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
            "OCR_ENABLED",
        ):
            os.environ.pop(variable, None)

        self.temp_dir.cleanup()

    async def test_pipeline_persists_ocr_fields_and_artifact_with_fake_ocr(self) -> None:
        application_id = await self._create_application()
        image_bytes = self._create_png_bytes()
        upload = await self.client.post(
            f"/applications/{application_id}/documents",
            files={"file": ("card.png", image_bytes, "image/png")},
        )
        self.assertEqual(upload.status_code, 201)
        document_id = upload.json()["document_id"]

        session = get_session_factory()()
        try:
            pipeline = PipelineService(
                session,
                storage_service=StorageService(),
                ocr_service=FakeOCRService(),
            )
            result = pipeline.process_document(document_id)
        finally:
            session.close()

        self.assertEqual(result.processing_status.value, "processed")
        self.assertEqual(result.page_count, 1)

        session = get_session_factory()()
        try:
            document = DocumentRepository(session).get_by_id(document_id)
            pages = DocumentPageRepository(session).list_by_document_id(document_id)
        finally:
            session.close()

        self.assertIsNotNone(document)
        self.assertAlmostEqual(document.ocr_confidence or 0.0, 0.87, places=2)
        self.assertEqual(document.document_type, "payslip")
        self.assertEqual(len(pages), 1)
        self.assertIn("Employee Name: Jane Doe", pages[0].ocr_text)
        self.assertIsNotNone(pages[0].ocr_json)
        self.assertEqual(pages[0].ocr_json["confidence"], 0.87)

        artifact = (
            self.storage_root
            / "loan-docs"
            / "applications"
            / application_id
            / "artifacts"
            / document_id
            / "ocr.json"
        )
        self.assertTrue(artifact.exists())
        self.assertIn("Employee Name: Jane Doe", artifact.read_text())

    async def _create_application(self) -> str:
        response = await self.client.post("/applications", json={"applicant_name": "OCR Tester"})
        self.assertEqual(response.status_code, 201)
        return response.json()["id"]

    def _create_png_bytes(self) -> bytes:
        image = np.full((200, 320, 3), 255, dtype=np.uint8)
        cv2.putText(
            image,
            "OCR TEST",
            (30, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 0),
            2,
            cv2.LINE_AA,
        )
        ok, encoded = cv2.imencode(".png", image)
        if not ok:
            raise AssertionError("Could not create OCR fixture image.")
        return encoded.tobytes()
