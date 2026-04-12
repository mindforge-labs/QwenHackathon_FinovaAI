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
from app.repositories.application_repository import ApplicationRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.review_action_repository import ReviewActionRepository
from app.services.ocr_service import OCRLine, OCRPageResult, OCRService
from app.services.pipeline_service import PipelineService


class FakeOCRService(OCRService):
    def __init__(self, text: str):
        self.text = text

    def run_page(self, *, image_bytes: bytes, page_number: int) -> OCRPageResult:
        line = OCRLine(
            text=self.text,
            bbox=[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]],
            confidence=0.93,
        )
        return OCRPageResult(
            page_number=page_number,
            text=self.text,
            lines=[line],
            confidence=0.93,
        )


class ReviewFlowTests(unittest.IsolatedAsyncioTestCase):
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

    async def test_review_update_persists_corrected_extraction_and_history(self) -> None:
        application_id, document_id = await self._prepare_processed_payslip()

        response = await self.client.patch(
            f"/documents/{document_id}/review",
            json={
                "reviewer_name": "Loan Officer",
                "comment": "Corrected employer name.",
                "corrected_json": {
                    "document_type": "payslip",
                    "employee_name": "Jane Doe",
                    "employer_name": "Finova Capital",
                    "pay_period": "03/2026",
                    "gross_salary": 1500,
                    "net_salary": 1200,
                },
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "needs_review")
        self.assertEqual(payload["extraction"]["normalized_extraction_json"]["employer_name"], "Finova Capital")
        self.assertEqual(payload["review_action"]["action"], "correct_fields")

        detail = await self.client.get(f"/documents/{document_id}")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["review_actions"][0]["reviewer_name"], "Loan Officer")
        self.assertEqual(
            detail.json()["extraction"]["normalized_extraction_json"]["employer_name"],
            "Finova Capital",
        )

        session = get_session_factory()()
        try:
            application = ApplicationRepository(session).get_by_id(application_id)
            review_actions = ReviewActionRepository(session).list_by_document_id(document_id)
        finally:
            session.close()

        self.assertIsNotNone(application)
        self.assertEqual(application.status, "under_review")
        self.assertEqual(len(review_actions), 1)

    async def test_decision_endpoint_approves_document_and_application(self) -> None:
        application_id, document_id = await self._prepare_processed_payslip()

        response = await self.client.post(
            f"/documents/{document_id}/decision",
            json={
                "reviewer_name": "Loan Officer",
                "action": "approve",
                "comment": "Looks good.",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "approved")
        self.assertEqual(payload["review_action"]["action"], "approve")

        detail = await self.client.get(f"/documents/{document_id}")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["status"], "approved")
        self.assertEqual(detail.json()["review_actions"][0]["action"], "approve")

        session = get_session_factory()()
        try:
            application = ApplicationRepository(session).get_by_id(application_id)
            document = DocumentRepository(session).get_by_id(document_id)
        finally:
            session.close()

        self.assertIsNotNone(application)
        self.assertEqual(application.status, "approved")
        self.assertEqual(document.status, "approved")

    async def _prepare_processed_payslip(self) -> tuple[str, str]:
        application_id = await self._create_application()
        image_bytes = self._create_png_bytes("PAYSLIP")

        upload = await self.client.post(
            f"/applications/{application_id}/documents",
            files={"file": ("payslip.png", image_bytes, "image/png")},
        )
        self.assertEqual(upload.status_code, 201)
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

        return application_id, document_id

    async def _create_application(self) -> str:
        response = await self.client.post("/applications", json={"applicant_name": "Reviewer"})
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
            raise AssertionError("Could not create review fixture image.")
        return encoded.tobytes()
