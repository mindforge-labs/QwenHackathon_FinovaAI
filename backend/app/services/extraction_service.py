from __future__ import annotations

from dataclasses import dataclass
import json
import re
from pathlib import Path

from app.core.exceptions import ProcessingFailureError
from app.services.llm_service import LLMService, build_llm_service

SCHEMA_DIR = Path(__file__).resolve().parents[3] / "docs" / "agent" / "schemas"
PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


@dataclass(slots=True)
class ExtractionResult:
    raw: dict
    normalized: dict
    source: str
    llm_attempt_count: int
    fallback_used: bool


class ExtractionService:
    def __init__(self, *, llm_service: LLMService | None = None):
        self.llm_service = llm_service or build_llm_service()

    def extract(self, *, document_type: str, ocr_text: str) -> ExtractionResult:
        if document_type == "unknown":
            raise ProcessingFailureError("Cannot extract fields for an unknown document type.")

        llm_attempt_count = 0
        fallback_used = False
        if self.llm_service.is_enabled():
            llm_result = self._extract_with_llm_retry(document_type=document_type, ocr_text=ocr_text)
            if llm_result is not None:
                return llm_result
            llm_attempt_count = 2
            fallback_used = True

        raw = self._rule_based_extract(document_type=document_type, ocr_text=ocr_text)
        normalized = self._validate_and_normalize(document_type=document_type, payload=raw)
        return ExtractionResult(
            raw=raw,
            normalized=normalized,
            source="rule_based",
            llm_attempt_count=llm_attempt_count,
            fallback_used=fallback_used,
        )

    def _extract_with_llm_retry(
        self,
        *,
        document_type: str,
        ocr_text: str,
    ) -> ExtractionResult | None:
        system_prompt = self._load_prompt(document_type)
        schema = self._load_schema(document_type)

        for attempt in range(1, 3):
            user_prompt = self._build_user_prompt(
                document_type=document_type,
                ocr_text=ocr_text,
                schema=schema,
                retry=attempt > 1,
            )
            try:
                llm_content = self.llm_service.extract_json(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                )
                raw = self._parse_llm_payload(llm_content)
                normalized = self._validate_and_normalize(document_type=document_type, payload=raw)
                return ExtractionResult(
                    raw=raw,
                    normalized=normalized,
                    source="llm",
                    llm_attempt_count=attempt,
                    fallback_used=False,
                )
            except ProcessingFailureError:
                continue

        return None

    def _rule_based_extract(self, *, document_type: str, ocr_text: str) -> dict:
        if document_type == "id_card":
            return self._extract_id_card(ocr_text)
        if document_type == "payslip":
            return self._extract_payslip(ocr_text)
        if document_type == "bank_statement":
            return self._extract_bank_statement(ocr_text)
        raise ProcessingFailureError(f"Unsupported document type '{document_type}' for extraction.")

    def _extract_id_card(self, ocr_text: str) -> dict:
        lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]
        full_name = None
        for line in lines:
            normalized = re.sub(r"\s+", " ", line.lower()).strip()
            if any(
                marker in normalized
                for marker in ("can cuoc", "căn cước", "cong dan", "công dân", "identity card")
            ):
                continue
            if re.fullmatch(r"[A-Z][A-Z\s]{4,}", line):
                full_name = line.title()
                break

        return {
            "document_type": "id_card",
            "full_name": full_name,
            "dob": self._find_first(r"(\d{2}[/-]\d{2}[/-]\d{4})", ocr_text),
            "id_number": self._find_first(r"\b(\d{12})\b", ocr_text),
            "address": self._find_label_value(ocr_text, ("address", "địa chỉ", "dia chi")),
            "issue_date": self._find_after_keywords(
                ocr_text,
                ("issue date", "ngày cấp", "ngay cap"),
                r"(\d{2}[/-]\d{2}[/-]\d{4})",
            ),
        }

    def _extract_payslip(self, ocr_text: str) -> dict:
        return {
            "document_type": "payslip",
            "employee_name": self._find_label_value(ocr_text, ("employee", "employee name")),
            "employer_name": self._find_label_value(ocr_text, ("employer", "company", "employer name")),
            "pay_period": self._find_after_keywords(
                ocr_text,
                ("pay period", "period", "salary period"),
                r"([A-Za-z]{3,9}\s+\d{4}|\d{2}[/-]\d{4}|\d{2}[/-]\d{2}[/-]\d{4})",
            ),
            "gross_salary": self._find_numeric_after_keywords(
                ocr_text,
                ("gross salary", "gross"),
            ),
            "net_salary": self._find_numeric_after_keywords(
                ocr_text,
                ("net salary", "net"),
            ),
        }

    def _extract_bank_statement(self, ocr_text: str) -> dict:
        return {
            "document_type": "bank_statement",
            "account_holder": self._find_label_value(
                ocr_text,
                ("account holder", "customer name", "account name"),
            ),
            "bank_name": self._find_label_value(ocr_text, ("bank name", "bank")),
            "account_number": self._find_after_keywords(
                ocr_text,
                ("account number", "account no", "acct number"),
                r"([0-9][0-9\s-]{5,})",
            ),
            "statement_period": self._find_after_keywords(
                ocr_text,
                ("statement period", "period"),
                r"([A-Za-z]{3,9}\s+\d{4}|\d{2}[/-]\d{4}|\d{2}[/-]\d{2}[/-]\d{4})",
            ),
            "ending_balance": self._find_numeric_after_keywords(
                ocr_text,
                ("ending balance", "closing balance", "balance"),
            ),
        }

    def _normalize(self, *, document_type: str, payload: dict) -> dict:
        normalized = dict(payload)

        for field in ("gross_salary", "net_salary", "ending_balance"):
            if field in normalized:
                normalized[field] = self._to_number(normalized.get(field))

        for field in ("account_number",):
            if field in normalized and isinstance(normalized.get(field), str):
                normalized[field] = re.sub(r"\s+", "", normalized[field])

        for field in ("full_name", "employee_name", "employer_name", "account_holder", "bank_name"):
            if field in normalized and isinstance(normalized.get(field), str):
                normalized[field] = re.sub(r"\s+", " ", normalized[field]).strip()

        return normalized

    def _validate_and_normalize(self, *, document_type: str, payload: dict) -> dict:
        self._validate_against_schema(document_type=document_type, payload=payload)
        normalized = self._normalize(document_type=document_type, payload=payload)
        self._validate_against_schema(document_type=document_type, payload=normalized)
        return normalized

    def _validate_against_schema(self, *, document_type: str, payload: dict) -> None:
        schema = self._load_schema(document_type)
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        if set(payload.keys()) != set(required):
            raise ProcessingFailureError(f"Extraction payload keys do not match schema for {document_type}.")

        expected_type = properties["document_type"]["const"]
        if payload.get("document_type") != expected_type:
            raise ProcessingFailureError(f"Extraction document_type must be '{expected_type}'.")

        for field, definition in properties.items():
            if field == "document_type":
                continue
            allowed_types = definition.get("type", [])
            value = payload.get(field)
            if value is None and "null" in allowed_types:
                continue
            if isinstance(value, str) and "string" in allowed_types:
                continue
            if isinstance(value, (int, float)) and "number" in allowed_types:
                continue
            raise ProcessingFailureError(f"Field '{field}' does not conform to schema type.")

    def _load_schema(self, document_type: str) -> dict:
        schema_path = SCHEMA_DIR / f"{document_type}.schema.json"
        return json.loads(schema_path.read_text())

    def _load_prompt(self, document_type: str) -> str:
        prompt_path = PROMPT_DIR / f"{document_type}_extraction.txt"
        return prompt_path.read_text(encoding="utf-8").strip()

    def _build_user_prompt(
        self,
        *,
        document_type: str,
        ocr_text: str,
        schema: dict,
        retry: bool,
    ) -> str:
        retry_instruction = ""
        if retry:
            retry_instruction = (
                "\nPrevious response was invalid. Return a single valid JSON object only."
                "\nDo not wrap JSON in markdown or prose."
            )

        return (
            f"Document type: {document_type}\n"
            f"Target schema:\n{json.dumps(schema, ensure_ascii=False)}\n\n"
            f"OCR text:\n{ocr_text}\n"
            f"{retry_instruction}"
        )

    def _parse_llm_payload(self, response_text: str) -> dict:
        candidate = response_text.strip()
        if candidate.startswith("```"):
            candidate = re.sub(r"^```(?:json)?\s*", "", candidate, flags=re.IGNORECASE)
            candidate = re.sub(r"\s*```$", "", candidate)

        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", candidate, re.DOTALL)
            if not match:
                raise ProcessingFailureError("LLM extraction did not return valid JSON.")
            try:
                payload = json.loads(match.group(0))
            except json.JSONDecodeError as exc:
                raise ProcessingFailureError("LLM extraction did not return valid JSON.") from exc

        if not isinstance(payload, dict):
            raise ProcessingFailureError("LLM extraction response must be a JSON object.")
        return payload

    def _find_first(self, pattern: str, text: str) -> str | None:
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _find_after_keywords(self, text: str, keywords: tuple[str, ...], pattern: str) -> str | None:
        for line in text.splitlines():
            lowered = line.lower()
            if any(keyword in lowered for keyword in keywords):
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        return None

    def _find_label_value(self, text: str, keywords: tuple[str, ...]) -> str | None:
        for line in text.splitlines():
            lowered = line.lower()
            for keyword in keywords:
                if keyword in lowered:
                    parts = re.split(r":", line, maxsplit=1)
                    if len(parts) == 2 and parts[1].strip():
                        return parts[1].strip()
        return None

    def _find_numeric_after_keywords(self, text: str, keywords: tuple[str, ...]) -> float | None:
        value = self._find_after_keywords(
            text,
            keywords,
            r"([0-9][0-9,.\s]*)",
        )
        return self._to_number(value)

    def _to_number(self, value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        cleaned = re.sub(r"[^\d.,-]", "", str(value))
        if not cleaned:
            return None
        cleaned = cleaned.replace(",", "")
        try:
            return float(cleaned)
        except ValueError:
            return None
