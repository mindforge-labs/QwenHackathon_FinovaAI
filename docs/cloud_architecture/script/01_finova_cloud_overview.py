"""Executive-level Alibaba Cloud overview for Finova AI."""

from diagrams import Cluster, Diagram
from diagrams.alibabacloud.application import ApiGateway
from diagrams.alibabacloud.compute import ElasticComputeService, ServerLoadBalancer, ServerlessAppEngine
from diagrams.alibabacloud.database import ApsaradbPostgresql, ApsaradbRedis
from diagrams.alibabacloud.network import Cdn, NatGateway, VirtualPrivateCloud
from diagrams.alibabacloud.security import CloudFirewall, SecurityCenter, WebApplicationFirewall
from diagrams.alibabacloud.storage import ObjectStorageService
from diagrams.alibabacloud.web import Dns, Domain
from diagrams.onprem.client import User, Users
from diagrams.onprem.network import Internet

from common import graph_attr, output_path


def build_diagram() -> None:
    with Diagram(
        "Finova AI - Cloud Overview",
        filename=output_path("01_finova_cloud_overview"),
        direction="LR",
        show=False,
        outformat="png",
        graph_attr=graph_attr(),
    ):
        borrowers = Users("Borrowers")
        reviewer = User("Loan reviewer")
        internet = Internet("Internet")

        domain = Domain("finova.example.com")
        dns = Dns("Alibaba Cloud DNS")
        cdn = Cdn("CDN")
        waf = WebApplicationFirewall("WAF")
        cloud_firewall = CloudFirewall("Cloud Firewall")
        slb = ServerLoadBalancer("Public SLB")

        borrowers >> internet
        reviewer >> internet
        internet >> domain >> dns >> cdn >> waf >> cloud_firewall >> slb

        with Cluster("Alibaba Cloud Production"):
            vpc = VirtualPrivateCloud("VPC")
            nat = NatGateway("NAT Gateway")

            with Cluster("Application"):
                frontend = ServerlessAppEngine("Next.js frontend")
                gateway = ApiGateway("API Gateway")
                backend = ServerlessAppEngine("FastAPI monolith")
                worker = ElasticComputeService("OCR / extraction worker")

            with Cluster("Data"):
                postgres = ApsaradbPostgresql("ApsaraDB PostgreSQL")
                redis = ApsaradbRedis("Redis")
                oss = ObjectStorageService("OSS")

            security = SecurityCenter("Security Center")

        slb >> vpc
        vpc >> frontend
        vpc >> gateway >> backend
        backend >> worker
        vpc >> nat

        backend >> postgres
        backend >> redis
        backend >> oss
        worker >> postgres
        worker >> redis
        worker >> oss
        security >> [backend, worker, postgres, oss]
