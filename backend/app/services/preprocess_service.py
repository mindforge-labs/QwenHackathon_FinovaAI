from __future__ import annotations

import cv2
import numpy as np

from app.core.exceptions import ProcessingFailureError


class PreprocessService:
    def normalize_image_to_jpeg(self, image_bytes: bytes) -> bytes:
        image = self._decode_image(image_bytes)
        return self._encode_jpeg(image)

    def preprocess_for_ocr(self, image_bytes: bytes) -> bytes:
        image = self._decode_image(image_bytes)
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(grayscale)
        enhanced = cv2.equalizeHist(denoised)
        return self._encode_jpeg(enhanced)

    def _decode_image(self, image_bytes: bytes):
        array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if image is None:
            raise ProcessingFailureError("Could not decode image bytes for preprocessing.")
        return image

    def _encode_jpeg(self, image) -> bytes:
        ok, encoded = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        if not ok:
            raise ProcessingFailureError("Could not encode processed image as JPEG.")
        return encoded.tobytes()
