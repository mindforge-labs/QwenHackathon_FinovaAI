from __future__ import annotations

import json
import logging
import os
import tempfile
import unittest
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from app.core.config import Settings, clear_settings_cache
from app.core.db import clear_db_state
from app.core.logging import JsonLogFormatter, configure_logging
from app.core.migrations import upgrade_database


class LoggingAndMigrationTests(unittest.TestCase):
    def tearDown(self) -> None:
        clear_db_state()
        clear_settings_cache()
        for variable in ("DATABASE_URL",):
            os.environ.pop(variable, None)

    def test_json_log_formatter_includes_structured_fields(self) -> None:
        formatter = JsonLogFormatter()
        record = logging.LogRecord(
            name="app.test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="structured event",
            args=(),
            exc_info=None,
        )
        record.event = "test_event"
        record.document_id = "doc-123"

        payload = json.loads(formatter.format(record))
        self.assertEqual(payload["message"], "structured event")
        self.assertEqual(payload["event"], "test_event")
        self.assertEqual(payload["document_id"], "doc-123")

    def test_configure_logging_sets_root_level(self) -> None:
        settings = Settings(
            app_name="Finova AI Backend",
            app_env="development",
            debug=False,
            auto_init_db=True,
            database_url="sqlite:///./finova.db",
            storage_backend="filesystem",
            filesystem_storage_root="./storage",
            minio_endpoint="minio:9000",
            minio_access_key="minioadmin",
            minio_secret_key="minioadmin",
            minio_bucket_name="loan-docs",
            minio_secure=False,
            ocr_enabled=False,
            ocr_language="en",
            ocr_use_angle_cls=True,
            llm_enabled=False,
            llm_base_url="https://api.openai.com/v1",
            llm_api_key="",
            llm_model="",
            llm_timeout_seconds=30.0,
            cors_origins=("http://localhost:3000",),
            auth_enabled=False,
            api_key="",
            log_level="WARNING",
            log_json=True,
            max_request_size_bytes=10 * 1024 * 1024,
            max_upload_size_bytes=8 * 1024 * 1024,
        )

        configure_logging(settings)
        self.assertEqual(logging.getLogger().level, logging.WARNING)

    def test_alembic_upgrade_creates_core_tables(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "alembic.db"
            os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

            alembic_cfg = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
            alembic_cfg.set_main_option(
                "script_location",
                str(Path(__file__).resolve().parents[2] / "alembic"),
            )

            command.upgrade(alembic_cfg, "head")

            self.assertTrue(db_path.exists())

    def test_upgrade_database_stamps_existing_legacy_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "legacy.db"
            os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

            engine = create_engine(f"sqlite:///{db_path}")
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "CREATE TABLE applications ("
                        "id VARCHAR(36) PRIMARY KEY,"
                        "applicant_name VARCHAR(255),"
                        "phone VARCHAR(64),"
                        "email VARCHAR(255),"
                        "status VARCHAR(32) NOT NULL,"
                        "created_at DATETIME NOT NULL,"
                        "updated_at DATETIME NOT NULL)"
                    )
                )

            clear_settings_cache()
            upgrade_database()

            inspector = inspect(engine)
            self.assertIn("alembic_version", inspector.get_table_names())
