from __future__ import annotations

import cv2
import fitz
import numpy as np

from app.core.exceptions import ProcessingFailureError


class PDFService:
    def render_pdf_to_jpeg_pages(self, pdf_bytes: bytes) -> list[bytes]:
        try:
            document = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as exc:
            raise ProcessingFailureError("Could not open PDF for page conversion.") from exc

        pages: list[bytes] = []
        try:
            for page in document:
                pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                buffer = np.frombuffer(pixmap.samples, dtype=np.uint8)
                rgb_image = buffer.reshape(pixmap.height, pixmap.width, pixmap.n)
                bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
                ok, encoded = cv2.imencode(".jpg", bgr_image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                if not ok:
                    raise ProcessingFailureError("Could not encode a rendered PDF page as JPEG.")
                pages.append(encoded.tobytes())
        finally:
            document.close()

        if not pages:
            raise ProcessingFailureError("PDF conversion produced no pages.")

        return pages
