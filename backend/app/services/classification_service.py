from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(slots=True)
class ClassificationResult:
    document_type: str
    confidence: float
    reason: str


class ClassificationService:
    def classify(self, ocr_text: str) -> ClassificationResult:
        normalized = ocr_text.lower()

        id_card_score = self._id_card_score(ocr_text, normalized)
        payslip_score = self._payslip_score(normalized)
        bank_statement_score = self._bank_statement_score(normalized)

        scored = [
            ("id_card", id_card_score, "matched id-card keywords or patterns"),
            ("payslip", payslip_score, "matched payslip keywords"),
            ("bank_statement", bank_statement_score, "matched bank statement keywords"),
        ]
        scored.sort(key=lambda item: item[1], reverse=True)
        best_type, best_score, reason = scored[0]

        if best_score <= 0:
            return ClassificationResult(
                document_type="unknown",
                confidence=0.0,
                reason="no rule-based classification matched",
            )

        return ClassificationResult(
            document_type=best_type,
            confidence=min(best_score / 5.0, 1.0),
            reason=reason,
        )

    def _id_card_score(self, ocr_text: str, normalized: str) -> int:
        score = 0
        if "căn cước" in normalized or "can cuoc" in normalized:
            score += 3
        if "công dân" in normalized or "cong dan" in normalized:
            score += 2
        if re.search(r"\b\d{12}\b", ocr_text):
            score += 2
        if "dob" in normalized or "date of birth" in normalized or "ngày sinh" in normalized:
            score += 1
        return score

    def _payslip_score(self, normalized: str) -> int:
        score = 0
        for keyword in (
            "salary",
            "basic salary",
            "net salary",
            "gross salary",
            "pay period",
            "employee",
            "employer",
        ):
            if keyword in normalized:
                score += 1
        return score

    def _bank_statement_score(self, normalized: str) -> int:
        score = 0
        for keyword in (
            "statement",
            "account number",
            "balance",
            "transaction",
            "bank",
        ):
            if keyword in normalized:
                score += 1
        return score
