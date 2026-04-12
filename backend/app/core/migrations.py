from __future__ import annotations

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.core.config import get_settings
from app.core.db import get_engine

logger = logging.getLogger(__name__)

ALEMBIC_CONFIG_PATH = Path(__file__).resolve().parents[2] / "alembic.ini"
ALEMBIC_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "alembic"
CORE_TABLES = {
    "applications",
    "documents",
    "document_pages",
    "extracted_fields",
    "review_actions",
    "validation_flags",
}


def upgrade_database() -> None:
    config = Config(str(ALEMBIC_CONFIG_PATH))
    config.set_main_option("script_location", str(ALEMBIC_SCRIPT_PATH))

    settings = get_settings()
    config.set_main_option("sqlalchemy.url", settings.database_url)

    engine = get_engine()
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    has_alembic_version = "alembic_version" in existing_tables
    has_legacy_schema = bool(CORE_TABLES.intersection(existing_tables))

    if has_legacy_schema and not has_alembic_version:
        logger.warning(
            "legacy schema detected without alembic version table; stamping head",
            extra={"event": "migration_legacy_schema_detected"},
        )
        command.stamp(config, "head")

    command.upgrade(config, "head")


if __name__ == "__main__":
    upgrade_database()
