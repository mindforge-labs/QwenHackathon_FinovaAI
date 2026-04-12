from __future__ import annotations

from datetime import datetime

from app.schemas.common import ORMModel


class ValidationFlagRead(ORMModel):
    id: str
    flag_code: str
    severity: str
    message: str
    field_name: str | None = None
    created_at: datetime
