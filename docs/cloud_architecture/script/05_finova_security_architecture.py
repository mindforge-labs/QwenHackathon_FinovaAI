"""Security control architecture for Finova AI on Alibaba Cloud."""

from diagrams import Cluster, Diagram
from diagrams.alibabacloud.application import LogService
from diagrams.alibabacloud.compute import ServerlessAppEngine
from diagrams.alibabacloud.database import ApsaradbPostgresql
from diagrams.alibabacloud.network import VirtualPrivateCloud
from diagrams.alibabacloud.security import (
    BastionHost,
    DataEncryptionService,
    SecurityCenter,
)
from diagrams.alibabacloud.storage import ObjectStorageService
from diagrams.onprem.client import User

from common import graph_attr, output_path


def build_diagram() -> None:
    with Diagram(
        "Finova AI - Security Architecture",
        filename=output_path("05_finova_security_architecture"),
        direction="LR",
        show=False,
        outformat="png",
        graph_attr=graph_attr(compact=True),
    ):
        admin = User("Ops / admin")

        with Cluster("Protected Runtime"):
            vpc = VirtualPrivateCloud("VPC")
            frontend = ServerlessAppEngine("Frontend runtime")
            backend = ServerlessAppEngine("Backend runtime")
            postgres = ApsaradbPostgresql("ApsaraDB PostgreSQL")
            oss = ObjectStorageService("OSS review assets")
            kms = DataEncryptionService("KMS")
            security_center = SecurityCenter("Security Center")
            sls = LogService("Audit / app logs")
            bastion = BastionHost("Bastion Host")

        vpc >> frontend
        vpc >> backend
        backend >> postgres
        backend >> oss
        kms >> [backend, postgres, oss]
        security_center >> [frontend, backend, postgres, oss]
        sls >> security_center
        admin >> bastion >> backend
        admin >> bastion >> postgres
