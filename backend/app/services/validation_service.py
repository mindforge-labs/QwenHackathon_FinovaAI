from __future__ import annotations

from datetime import datetime, timezone
import re
from difflib import SequenceMatcher
import unicodedata


class ValidationService:
    def build_processing_flags(
        self,
        *,
        document_type: str,
        classification_confidence: float,
        ocr_text: str,
        ocr_confidence: float | None,
    ) -> list[dict]:
        flags: list[dict] = []

        if not ocr_text.strip():
            flags.append(
                {
                    "flag_code": "EMPTY_OCR",
                    "severity": "error",
                    "message": "OCR returned no text for this document.",
                    "field_name": None,
                }
            )

        if ocr_confidence is not None and ocr_confidence < 0.5:
            flags.append(
                {
                    "flag_code": "LOW_OCR_CONFIDENCE",
                    "severity": "warning",
                    "message": "OCR confidence is low and should be reviewed manually.",
                    "field_name": None,
                }
            )

        if document_type == "unknown":
            flags.append(
                {
                    "flag_code": "UNKNOWN_DOCUMENT_TYPE",
                    "severity": "warning",
                    "message": "Document type could not be classified confidently.",
                    "field_name": None,
                }
            )
        elif classification_confidence < 0.5:
            flags.append(
                {
                    "flag_code": "LOW_CLASSIFICATION_CONFIDENCE",
                    "severity": "warning",
                    "message": "Document classification confidence is low.",
                    "field_name": "document_type",
                }
            )

        return flags

    def build_extraction_flags(
        self,
        *,
        document_type: str,
        normalized_extraction: dict | None,
        extraction_confidence: float | None,
        extraction_source: str | None = None,
        llm_attempt_count: int = 0,
        fallback_used: bool = False,
    ) -> list[dict]:
        flags: list[dict] = []
        payload = normalized_extraction or {}

        if llm_attempt_count > 1:
            flags.append(
                {
                    "flag_code": "LLM_EXTRACTION_RETRIED",
                    "severity": "warning",
                    "message": "LLM extraction needed a retry before returning valid JSON.",
                    "field_name": None,
                }
            )

        if fallback_used:
            flags.append(
                {
                    "flag_code": "LLM_EXTRACTION_FALLBACK",
                    "severity": "warning",
                    "message": "LLM extraction failed and the pipeline fell back to rule-based extraction.",
                    "field_name": None,
                }
            )

        for field_name in self._required_review_fields(document_type):
            if payload.get(field_name) in (None, ""):
                flags.append(
                    {
                        "flag_code": "MISSING_REQUIRED_FIELD",
                        "severity": "warning",
                        "message": f"Important field '{field_name}' is missing from extraction output.",
                        "field_name": field_name,
                    }
                )

        if document_type == "id_card":
            flags.extend(self._validate_id_card(payload))
        elif document_type == "payslip":
            flags.extend(self._validate_payslip(payload))
        elif document_type == "bank_statement":
            flags.extend(self._validate_bank_statement(payload))

        if extraction_confidence is not None and extraction_confidence < 0.6:
            flags.append(
                {
                    "flag_code": "LOW_EXTRACTION_CONFIDENCE",
                    "severity": "warning",
                    "message": "Extraction confidence is low and should be reviewed manually.",
                    "field_name": None,
                }
            )

        return flags

    def compute_extraction_confidence(
        self,
        *,
        document_type: str,
        normalized_extraction: dict | None,
        classification_confidence: float,
        ocr_confidence: float | None,
        extraction_source: str | None = None,
        llm_attempt_count: int = 0,
        fallback_used: bool = False,
    ) -> float | None:
        if not normalized_extraction:
            return None

        review_fields = self._required_review_fields(document_type)
        if not review_fields:
            return None

        filled_fields = sum(
            1 for field_name in review_fields if normalized_extraction.get(field_name) not in (None, "")
        )
        completeness_score = filled_fields / len(review_fields)
        ocr_score = max(min(float(ocr_confidence or 0.0), 1.0), 0.0)
        classification_score = max(min(float(classification_confidence), 1.0), 0.0)

        confidence = (0.5 * completeness_score) + (0.25 * ocr_score) + (0.25 * classification_score)
        if extraction_source == "rule_based":
            confidence -= 0.05
        if llm_attempt_count > 1:
            confidence -= 0.05
        if fallback_used:
            confidence -= 0.15
        confidence = max(min(confidence, 1.0), 0.0)
        return round(confidence, 4)

    def build_cross_document_flags(self, documents: list) -> dict[str, list[dict]]:
        flags_by_document: dict[str, list[dict]] = {document.id: [] for document in documents}
        extracted_names: dict[str, tuple[str, str] | None] = {
            document.id: self._extract_name_for_cross_check(document)
            for document in documents
        }

        id_card_documents = [
            document for document in documents if getattr(document, "document_type", None) == "id_card"
        ]

        for id_document in id_card_documents:
            id_name_info = extracted_names.get(id_document.id)
            if id_name_info is None:
                continue

            for target_type, target_field in (
                ("payslip", "employee_name"),
                ("bank_statement", "account_holder"),
            ):
                for other_document in documents:
                    if getattr(other_document, "document_type", None) != target_type:
                        continue

                    other_name_info = extracted_names.get(other_document.id)
                    if other_name_info is None:
                        continue

                    if self._names_match(id_name_info[0], other_name_info[0]):
                        continue

                    flags_by_document[id_document.id].append(
                        self._flag(
                            code="NAME_MISMATCH",
                            severity="warning",
                            message=(
                                f"Name mismatch detected between id_card full_name and "
                                f"{target_type} {target_field}."
                            ),
                            field_name="full_name",
                        )
                    )
                    flags_by_document[other_document.id].append(
                        self._flag(
                            code="NAME_MISMATCH",
                            severity="warning",
                            message=(
                                f"Name mismatch detected between {target_type} {target_field} "
                                f"and id_card full_name."
                            ),
                            field_name=target_field,
                        )
                    )

        return {
            document_id: self._dedupe_flags(flags)
            for document_id, flags in flags_by_document.items()
            if flags
        }

    def _required_review_fields(self, document_type: str) -> tuple[str, ...]:
        if document_type == "id_card":
            return ("full_name", "id_number")
        if document_type == "payslip":
            return ("employee_name", "net_salary")
        if document_type == "bank_statement":
            return ("account_holder", "account_number")
        return ()

    def _extract_name_for_cross_check(self, document) -> tuple[str, str] | None:
        if not getattr(document, "extracted_fields", None):
            return None

        payload = document.extracted_fields[0].normalized_extraction_json or {}
        if document.document_type == "id_card":
            value = payload.get("full_name")
            field_name = "full_name"
        elif document.document_type == "payslip":
            value = payload.get("employee_name")
            field_name = "employee_name"
        elif document.document_type == "bank_statement":
            value = payload.get("account_holder")
            field_name = "account_holder"
        else:
            return None

        if not value:
            return None

        normalized = self._normalize_name(str(value))
        if not normalized:
            return None

        return normalized, field_name

    def _normalize_name(self, value: str) -> str:
        text = unicodedata.normalize("NFKD", value)
        text = "".join(char for char in text if not unicodedata.combining(char))
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _names_match(self, left: str, right: str) -> bool:
        if not left or not right:
            return True
        if left == right:
            return True

        similarity = SequenceMatcher(None, left, right).ratio()
        return similarity >= 0.85

    def _dedupe_flags(self, flags: list[dict]) -> list[dict]:
        seen: set[tuple[str, str | None, str]] = set()
        deduped: list[dict] = []
        for flag in flags:
            key = (flag["flag_code"], flag.get("field_name"), flag["message"])
            if key in seen:
                continue
            seen.add(key)
            deduped.append(flag)
        return deduped

    def _validate_id_card(self, payload: dict) -> list[dict]:
        flags: list[dict] = []

        id_number = payload.get("id_number")
        if id_number is not None and not re.fullmatch(r"\d{12}", str(id_number)):
            flags.append(
                self._flag(
                    code="INVALID_ID_NUMBER",
                    severity="error",
                    message="ID number must contain exactly 12 digits when present.",
                    field_name="id_number",
                )
            )

        for field_name in ("dob", "issue_date"):
            value = payload.get(field_name)
            if value is None:
                continue
            parsed = self._parse_date(str(value))
            if parsed is None:
                flags.append(
                    self._flag(
                        code="INVALID_DATE",
                        severity="warning",
                        message=f"Field '{field_name}' is not a valid date.",
                        field_name=field_name,
                    )
                )
                continue
            if field_name == "issue_date" and parsed > datetime.now(timezone.utc).date():
                flags.append(
                    self._flag(
                        code="FUTURE_DATE",
                        severity="error",
                        message="Issue date cannot be in the future.",
                        field_name=field_name,
                    )
                )

        return flags

    def _validate_payslip(self, payload: dict) -> list[dict]:
        flags: list[dict] = []
        gross_salary = payload.get("gross_salary")
        net_salary = payload.get("net_salary")

        if gross_salary is not None and float(gross_salary) <= 0:
            flags.append(
                self._flag(
                    code="INVALID_GROSS_SALARY",
                    severity="error",
                    message="Gross salary must be a positive number.",
                    field_name="gross_salary",
                )
            )

        if net_salary is not None and float(net_salary) <= 0:
            flags.append(
                self._flag(
                    code="INVALID_NET_SALARY",
                    severity="error",
                    message="Net salary must be a positive number.",
                    field_name="net_salary",
                )
            )

        if gross_salary is not None and net_salary is not None and float(net_salary) > float(gross_salary):
            flags.append(
                self._flag(
                    code="SALARY_INCONSISTENCY",
                    severity="error",
                    message="Net salary cannot be greater than gross salary.",
                    field_name="net_salary",
                )
            )

        pay_period = payload.get("pay_period")
        if pay_period is not None and self._parse_period(str(pay_period)) is None:
            flags.append(
                self._flag(
                    code="INVALID_PAY_PERIOD",
                    severity="warning",
                    message="Pay period is not in a recognized month or date format.",
                    field_name="pay_period",
                )
            )

        return flags

    def _validate_bank_statement(self, payload: dict) -> list[dict]:
        flags: list[dict] = []
        account_number = payload.get("account_number")
        if account_number is not None:
            normalized = re.sub(r"[\s-]+", "", str(account_number))
            if not re.fullmatch(r"\d{6,}", normalized):
                flags.append(
                    self._flag(
                        code="INVALID_ACCOUNT_NUMBER",
                        severity="warning",
                        message="Account number does not match the expected numeric format.",
                        field_name="account_number",
                    )
                )

        return flags

    def _parse_date(self, value: str):
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        return None

    def _parse_period(self, value: str):
        for fmt in ("%m/%Y", "%m-%Y", "%b %Y", "%B %Y", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        return None

    def _flag(
        self,
        *,
        code: str,
        severity: str,
        message: str,
        field_name: str | None,
    ) -> dict:
        return {
            "flag_code": code,
            "severity": severity,
            "message": message,
            "field_name": field_name,
        }
