from __future__ import annotations

import hmac

from fastapi import Header, HTTPException, status

from app.core.config import get_settings


async def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None),
) -> None:
    settings = get_settings()
    if not settings.auth_enabled:
        return

    expected_key = settings.api_key.strip()
    provided_key = _extract_api_key(x_api_key=x_api_key, authorization=authorization)
    if not provided_key or not hmac.compare_digest(provided_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )


def _extract_api_key(*, x_api_key: str | None, authorization: str | None) -> str | None:
    if x_api_key and x_api_key.strip():
        return x_api_key.strip()

    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
        return token or None

    return None
