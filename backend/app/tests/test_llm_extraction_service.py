from __future__ import annotations

import unittest

from app.services.extraction_service import ExtractionService


class FakeLLMService:
    def __init__(self, responses: list[str]):
        self.responses = responses
        self.calls = 0

    def is_enabled(self) -> bool:
        return True

    def extract_json(self, *, system_prompt: str, user_prompt: str) -> str:
        response = self.responses[self.calls]
        self.calls += 1
        return response


class ExtractionServiceLLMTests(unittest.TestCase):
    def test_llm_extraction_uses_valid_json_response(self) -> None:
        service = ExtractionService(
            llm_service=FakeLLMService(
                [
                    (
                        '{"document_type":"payslip","employee_name":"Jane Doe",'
                        '"employer_name":"Finova AI","pay_period":"03/2026",'
                        '"gross_salary":1500,"net_salary":1200}'
                    )
                ]
            )
        )

        result = service.extract(
            document_type="payslip",
            ocr_text="Employee Name: Jane Doe\nGross Salary: 1500\nNet Salary: 1200",
        )

        self.assertEqual(result.source, "llm")
        self.assertEqual(result.llm_attempt_count, 1)
        self.assertFalse(result.fallback_used)
        self.assertEqual(result.normalized["employee_name"], "Jane Doe")
        self.assertEqual(result.normalized["net_salary"], 1200.0)

    def test_llm_extraction_retries_once_on_invalid_json_then_succeeds(self) -> None:
        service = ExtractionService(
            llm_service=FakeLLMService(
                [
                    "not-json",
                    (
                        '{"document_type":"payslip","employee_name":"Jane Doe",'
                        '"employer_name":"Finova AI","pay_period":"03/2026",'
                        '"gross_salary":1500,"net_salary":1200}'
                    ),
                ]
            )
        )

        result = service.extract(
            document_type="payslip",
            ocr_text="Employee Name: Jane Doe\nGross Salary: 1500\nNet Salary: 1200",
        )

        self.assertEqual(result.source, "llm")
        self.assertEqual(result.llm_attempt_count, 2)
        self.assertFalse(result.fallback_used)

    def test_llm_extraction_falls_back_to_rule_based_after_failed_retry(self) -> None:
        service = ExtractionService(
            llm_service=FakeLLMService(
                [
                    "not-json",
                    '{"document_type":"payslip","employee_name":123}',
                ]
            )
        )

        result = service.extract(
            document_type="payslip",
            ocr_text=(
                "Employee Name: Jane Doe\n"
                "Employer: Finova AI\n"
                "Pay Period: 03/2026\n"
                "Gross Salary: 1500\n"
                "Net Salary: 1200\n"
            ),
        )

        self.assertEqual(result.source, "rule_based")
        self.assertEqual(result.llm_attempt_count, 2)
        self.assertTrue(result.fallback_used)
        self.assertEqual(result.normalized["employee_name"], "Jane Doe")
