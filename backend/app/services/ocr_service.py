from __future__ import annotations

from dataclasses import asdict, dataclass

import cv2
import numpy as np

from app.core.config import Settings, get_settings
from app.core.exceptions import ProcessingFailureError


@dataclass(slots=True)
class OCRLine:
    text: str
    bbox: list[list[float]]
    confidence: float


@dataclass(slots=True)
class OCRPageResult:
    page_number: int
    text: str
    lines: list[OCRLine]
    confidence: float

    def as_json(self) -> dict:
        return {
            "page_number": self.page_number,
            "text": self.text,
            "confidence": self.confidence,
            "lines": [asdict(line) for line in self.lines],
        }


class OCRService:
    def run_page(self, *, image_bytes: bytes, page_number: int) -> OCRPageResult:
        raise NotImplementedError


class DisabledOCRService(OCRService):
    def run_page(self, *, image_bytes: bytes, page_number: int) -> OCRPageResult:
        return OCRPageResult(page_number=page_number, text="", lines=[], confidence=0.0)


class PaddleOCRService(OCRService):
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self._engine = None

    def run_page(self, *, image_bytes: bytes, page_number: int) -> OCRPageResult:
        image = self._decode_image(image_bytes)
        engine = self._get_engine()

        try:
            raw_result = engine.ocr(image, cls=self.settings.ocr_use_angle_cls)
        except Exception as exc:
            raise ProcessingFailureError("PaddleOCR could not process the page image.") from exc

        lines: list[OCRLine] = []
        for block in raw_result or []:
            for item in block or []:
                if not item or len(item) < 2:
                    continue
                bbox, text_info = item
                text = str(text_info[0]).strip()
                confidence = float(text_info[1]) if len(text_info) > 1 else 0.0
                lines.append(
                    OCRLine(
                        text=text,
                        bbox=[[float(value) for value in point] for point in bbox],
                        confidence=confidence,
                    )
                )

        combined_text = "\n".join(line.text for line in lines if line.text)
        confidence = self._aggregate_confidence(lines)
        return OCRPageResult(
            page_number=page_number,
            text=combined_text,
            lines=lines,
            confidence=confidence,
        )

    def _get_engine(self):
        if self._engine is not None:
            return self._engine

        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:
            raise ProcessingFailureError(
                "PaddleOCR is not installed. Install backend requirements and enable OCR."
            ) from exc

        self._engine = PaddleOCR(
            use_angle_cls=self.settings.ocr_use_angle_cls,
            lang=self.settings.ocr_language,
            show_log=False,
        )
        return self._engine

    def _decode_image(self, image_bytes: bytes):
        array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if image is None:
            raise ProcessingFailureError("Could not decode processed page image for OCR.")
        return image

    def _aggregate_confidence(self, lines: list[OCRLine]) -> float:
        if not lines:
            return 0.0

        weighted_score = 0.0
        total_weight = 0
        for line in lines:
            weight = max(len(line.text.strip()), 1)
            weighted_score += line.confidence * weight
            total_weight += weight

        return weighted_score / total_weight if total_weight else 0.0


def build_ocr_service(settings: Settings | None = None) -> OCRService:
    resolved_settings = settings or get_settings()
    if not resolved_settings.ocr_enabled:
        return DisabledOCRService()
    return PaddleOCRService(resolved_settings)
