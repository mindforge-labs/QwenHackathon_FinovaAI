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
from app.services.ocr_service import OCRLine, OCRPageResult, OCRService
from app.services.pipeline_service import PipelineService


class FakeOCRService(OCRService):
    def __init__(self, text: str, confidence: float = 0.94):
        self.text = text
        self.confidence = confidence

    def run_page(self, *, image_bytes: bytes, page_number: int) -> OCRPageResult:
        line = OCRLine(
            text=self.text,
            bbox=[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]],
            confidence=self.confidence,
        )
        return OCRPageResult(
            page_number=page_number,
            text=self.text,
            lines=[line],
            confidence=self.confidence,
        )


class CrossDocumentValidationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test.db"
        self.storage_root = Path(self.temp_dir.name) / "storage"

        os.environ["DATABASE_URL"] = f"sqlite:///{self.database_path}"
        os.environ["STORAGE_BACKEND"] = "filesystem"
        os.environ["FILESYSTEM_STORAGE_ROOT"] = str(self.storage_root)
        os.environ["MINIO_BUCKET_NAME"] = "loan-docs"
        os.environ["OCR_ENABLED"] = "false"
        os.environ["LLM_ENABLED"] = "false"

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
            "LLM_ENABLED",
        ):
            os.environ.pop(variable, None)

        self.temp_dir.cleanup()

    async def test_name_mismatch_flags_id_card_and_payslip(self) -> None:
        application_id = await self._create_application()
        id_document_id = await self._upload_document(application_id, "id.png")
        payslip_document_id = await self._upload_document(application_id, "payslip.png")

        await self._process_document(
            id_document_id,
            (
                "CAN CUOC CONG DAN\n"
                "NGUYEN VAN A\n"
                "DOB: 01/01/1990\n"
                "123456789012\n"
                "Address: 1 Main Street\n"
                "Issue Date: 01/01/2020\n"
            ),
        )
        await self._process_document(
            payslip_document_id,
            (
                "Employee Name: Tran Thi B\n"
                "Employer: Finova AI\n"
                "Pay Period: 03/2026\n"
                "Gross Salary: 1500\n"
                "Net Salary: 1200\n"
                "salary net salary gross salary pay period"
            ),
        )

        id_detail = await self.client.get(f"/documents/{id_document_id}")
        payslip_detail = await self.client.get(f"/documents/{payslip_document_id}")

        self.assertEqual(id_detail.status_code, 200)
        self.assertEqual(payslip_detail.status_code, 200)
        self.assertTrue(
            any(flag["flag_code"] == "NAME_MISMATCH" for flag in id_detail.json()["validation_flags"])
        )
        self.assertTrue(
            any(flag["flag_code"] == "NAME_MISMATCH" for flag in payslip_detail.json()["validation_flags"])
        )
        self.assertEqual(payslip_detail.json()["status"], "needs_review")

    async def test_review_correction_clears_name_mismatch(self) -> None:
        application_id = await self._create_application()
        id_document_id = await self._upload_document(application_id, "id.png")
        payslip_document_id = await self._upload_document(application_id, "payslip.png")

        await self._process_document(
            id_document_id,
            (
                "CAN CUOC CONG DAN\n"
                "NGUYEN VAN A\n"
                "DOB: 01/01/1990\n"
                "123456789012\n"
                "Address: 1 Main Street\n"
                "Issue Date: 01/01/2020\n"
            ),
        )
        await self._process_document(
            payslip_document_id,
            (
                "Employee Name: Tran Thi B\n"
                "Employer: Finova AI\n"
                "Pay Period: 03/2026\n"
                "Gross Salary: 1500\n"
                "Net Salary: 1200\n"
                "salary net salary gross salary pay period"
            ),
        )

        review = await self.client.patch(
            f"/documents/{payslip_document_id}/review",
            json={
                "reviewer_name": "Loan Officer",
                "comment": "Adjusted employee name to match ID card.",
                "corrected_json": {
                    "document_type": "payslip",
                    "employee_name": "Nguyen Van A",
                    "employer_name": "Finova AI",
                    "pay_period": "03/2026",
                    "gross_salary": 1500,
                    "net_salary": 1200,
                },
            },
        )
        self.assertEqual(review.status_code, 200)

        id_detail = await self.client.get(f"/documents/{id_document_id}")
        payslip_detail = await self.client.get(f"/documents/{payslip_document_id}")

        self.assertFalse(
            any(flag["flag_code"] == "NAME_MISMATCH" for flag in id_detail.json()["validation_flags"])
        )
        self.assertFalse(
            any(flag["flag_code"] == "NAME_MISMATCH" for flag in payslip_detail.json()["validation_flags"])
        )

    async def _create_application(self) -> str:
        response = await self.client.post("/applications", json={"applicant_name": "Cross Check"})
        self.assertEqual(response.status_code, 201)
        return response.json()["id"]

    async def _upload_document(self, application_id: str, filename: str) -> str:
        response = await self.client.post(
            f"/applications/{application_id}/documents",
            files={"file": (filename, self._create_png_bytes(filename), "image/png")},
        )
        self.assertEqual(response.status_code, 201)
        return response.json()["document_id"]

    async def _process_document(self, document_id: str, ocr_text: str) -> None:
        session = get_session_factory()()
        try:
            pipeline = PipelineService(session, ocr_service=FakeOCRService(ocr_text))
            result = pipeline.process_document(document_id)
            self.assertIn(result.processing_status.value, {"processed", "needs_review"})
        finally:
            session.close()

    def _create_png_bytes(self, text: str) -> bytes:
        image = np.full((240, 640, 3), 255, dtype=np.uint8)
        cv2.putText(
            image,
            text[:12],
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 0),
            2,
            cv2.LINE_AA,
        )
        ok, encoded = cv2.imencode(".png", image)
        if not ok:
            raise AssertionError("Could not create cross-document fixture image.")
        return encoded.tobytes()
