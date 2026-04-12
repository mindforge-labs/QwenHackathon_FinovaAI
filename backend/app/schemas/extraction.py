from __future__ import annotations

from datetime import datetime

from app.schemas.common import ORMModel


class ExtractionRead(ORMModel):
    id: str
    schema_version: str
    raw_extraction_json: dict
    normalized_extraction_json: dict
    created_at: datetime
    updated_at: datetime
