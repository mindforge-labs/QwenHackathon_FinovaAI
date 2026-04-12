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
from app.main import create_app
from app.repositories.document_repository import DocumentRepository
from app.services.ocr_service import OCRLine, OCRPageResult, OCRService
from app.services.pipeline_service import PipelineService


class FakeOCRService(OCRService):
    def __init__(self, text: str):
        self.text = text

    def run_page(self, *, image_bytes: bytes, page_number: int) -> OCRPageResult:
        line = OCRLine(
            text=self.text,
            bbox=[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]],
            confidence=0.92,
        )
        return OCRPageResult(
            page_number=page_number,
            text=self.text,
            lines=[line],
            confidence=0.92,
        )


class ExtractionPipelineTests(unittest.IsolatedAsyncioTestCase):
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

    async def test_payslip_extraction_persists_structured_payload(self) -> None:
        application_id = await self._create_application()
        image_bytes = self._create_png_bytes("PAYSLIP")

        upload = await self.client.post(
            f"/applications/{application_id}/documents",
            files={"file": ("payslip.png", image_bytes, "image/png")},
        )
        document_id = upload.json()["document_id"]

        ocr_text = (
            "Employee Name: Jane Doe\n"
            "Employer: Finova AI\n"
            "Pay Period: 03/2026\n"
            "Gross Salary: 1500\n"
            "Net Salary: 1200\n"
            "salary net salary gross salary pay period"
        )
        session = get_session_factory()()
        try:
            pipeline = PipelineService(session, ocr_service=FakeOCRService(ocr_text))
            result = pipeline.process_document(document_id)
            self.assertEqual(result.processing_status.value, "processed")
        finally:
            session.close()

        detail = await self.client.get(f"/documents/{document_id}")
        self.assertEqual(detail.status_code, 200)
        payload = detail.json()
        self.assertEqual(payload["document_type"], "payslip")
        self.assertIsNotNone(payload["extraction"])
        self.assertEqual(payload["extraction"]["normalized_extraction_json"]["employee_name"], "Jane Doe")
        self.assertEqual(payload["extraction"]["normalized_extraction_json"]["employer_name"], "Finova AI")
        self.assertEqual(payload["extraction"]["normalized_extraction_json"]["gross_salary"], 1500.0)
        self.assertEqual(payload["extraction"]["normalized_extraction_json"]["net_salary"], 1200.0)
        self.assertGreater(payload["extraction_confidence"], 0.8)
        self.assertFalse(any(flag["severity"] == "error" for flag in payload["validation_flags"]))

        artifact = (
            self.storage_root
            / "loan-docs"
            / "applications"
            / application_id
            / "artifacts"
            / document_id
            / "extraction.json"
        )
        self.assertTrue(artifact.exists())
        self.assertIn("Jane Doe", artifact.read_text())

        session = get_session_factory()()
        try:
            document = DocumentRepository(session).get_by_id(document_id)
        finally:
            session.close()

        self.assertIsNotNone(document)
        self.assertTrue(document.extracted_fields)
        self.assertEqual(document.extracted_fields[0].normalized_extraction_json["pay_period"], "03/2026")
        self.assertIsNotNone(document.extraction_confidence)

    async def _create_application(self) -> str:
        response = await self.client.post("/applications", json={"applicant_name": "Extractor"})
        self.assertEqual(response.status_code, 201)
        return response.json()["id"]

    def _create_png_bytes(self, text: str) -> bytes:
        image = np.full((240, 640, 3), 255, dtype=np.uint8)
        cv2.putText(
            image,
            text,
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 0, 0),
            2,
            cv2.LINE_AA,
        )
        ok, encoded = cv2.imencode(".png", image)
        if not ok:
            raise AssertionError("Could not create extraction fixture image.")
        return encoded.tobytes()
