"""Asynchronous upload-to-processing architecture for Finova AI."""

from diagrams import Cluster, Diagram
from diagrams.alibabacloud.application import ApiGateway, LogService, MessageNotificationService
from diagrams.alibabacloud.compute import AutoScaling, ElasticComputeService, FunctionCompute, ServerlessAppEngine
from diagrams.alibabacloud.database import ApsaradbPostgresql, ApsaradbRedis
from diagrams.alibabacloud.storage import ObjectStorageService
from diagrams.onprem.client import User
from diagrams.programming.language import Python

from common import graph_attr, output_path


def build_diagram() -> None:
    with Diagram(
        "Finova AI - Async Processing Architecture",
        filename=output_path("02_finova_async_processing_architecture"),
        direction="LR",
        show=False,
        outformat="png",
        graph_attr=graph_attr(compact=True),
    ):
        reviewer = User("Reviewer")

        with Cluster("Synchronous Request Path"):
            frontend = ServerlessAppEngine("Next.js UI")
            gateway = ApiGateway("API Gateway")
            backend = ServerlessAppEngine("FastAPI API")

        with Cluster("Asynchronous Processing"):
            queue = MessageNotificationService("MNS queue")
            hook = FunctionCompute("Trigger / callback")
            autoscaling = AutoScaling("Auto Scaling")
            worker = ElasticComputeService("Pipeline worker")
            ocr = Python("PaddleOCR + OpenCV")
            extraction = Python("DashScope client")
            validation = Python("Validation engine")

        with Cluster("Shared State"):
            oss = ObjectStorageService("OSS")
            postgres = ApsaradbPostgresql("PostgreSQL")
            redis = ApsaradbRedis("Redis")
            sls = LogService("SLS")

        reviewer >> frontend >> gateway >> backend
        backend >> oss
        backend >> postgres
        backend >> queue
        backend >> sls

        hook >> queue
        queue >> autoscaling >> worker
        worker >> ocr >> extraction >> validation
        validation >> postgres
        worker >> oss
        worker >> redis
        worker >> sls
        frontend >> oss
