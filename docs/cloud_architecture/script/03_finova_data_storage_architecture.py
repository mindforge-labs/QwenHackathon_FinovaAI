"""Data placement and artifact persistence architecture for Finova AI."""

from diagrams import Diagram, Edge
from diagrams.alibabacloud.database import (
    ApsaradbPostgresql,
    ApsaradbRedis,
    DataManagementService,
    DatabaseBackupService,
)
from diagrams.alibabacloud.security import DataEncryptionService
from diagrams.alibabacloud.storage import HybridBackupRecovery, ObjectStorageService
from diagrams.programming.framework import Fastapi
from diagrams.programming.language import Python

from common import graph_attr, output_path


def build_diagram() -> None:
    with Diagram(
        "Finova AI - Data Storage Architecture",
        filename=output_path("03_finova_data_storage_architecture"),
        direction="LR",
        show=False,
        outformat="png",
        graph_attr={**graph_attr(compact=True), "size": "18,6!"},
    ):
        api = Fastapi("FastAPI API")
        worker = Python("Processing worker")
        postgres = ApsaradbPostgresql("ApsaraDB PostgreSQL")
        redis = ApsaradbRedis("Redis cache")
        oss_raw = ObjectStorageService("OSS raw uploads")
        oss_pages = ObjectStorageService("OSS page images")
        oss_artifacts = ObjectStorageService("OSS OCR + extraction artifacts")
        kms = DataEncryptionService("KMS")
        dms = DataManagementService("DMS")
        dbs = DatabaseBackupService("DBS")
        hbr = HybridBackupRecovery("HBR")

        api >> Edge(style="invis", weight="10") >> worker
        worker >> Edge(style="invis", weight="10") >> postgres
        postgres >> Edge(style="invis", weight="10") >> redis
        redis >> Edge(style="invis", weight="10") >> oss_raw
        oss_raw >> Edge(style="invis", weight="10") >> oss_pages
        oss_pages >> Edge(style="invis", weight="10") >> oss_artifacts
        oss_artifacts >> Edge(style="invis", weight="10") >> kms
        dms >> Edge(style="invis", weight="10") >> dbs
        dbs >> Edge(style="invis", weight="10") >> hbr

        api >> postgres
        api >> redis
        api >> oss_raw

        worker >> postgres
        worker >> redis
        worker >> oss_pages
        worker >> oss_artifacts

        dms >> postgres
        dbs >> postgres
        hbr >> oss_artifacts
        kms >> [postgres, oss_raw, oss_pages, oss_artifacts]
