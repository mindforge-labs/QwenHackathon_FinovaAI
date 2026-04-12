from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        content_length = request.headers.get("content-length")

        if content_length is not None:
            try:
                content_length_value = int(content_length)
            except ValueError:
                content_length_value = None

            if (
                content_length_value is not None
                and content_length_value > settings.max_request_size_bytes
            ):
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request body exceeds the configured size limit."},
                )

        return await call_next(request)
