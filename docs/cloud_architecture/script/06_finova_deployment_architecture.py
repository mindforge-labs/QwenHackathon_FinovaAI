"""Deployment and delivery architecture for Finova AI."""

from diagrams import Diagram, Edge
from diagrams.alibabacloud.application import CodePipeline
from diagrams.alibabacloud.compute import ContainerRegistry, ElasticComputeService, ResourceOrchestrationService, ServerlessAppEngine
from diagrams.alibabacloud.network import VirtualPrivateCloud
from diagrams.onprem.vcs import Git

from common import graph_attr, output_path


def build_diagram() -> None:
    with Diagram(
        "Finova AI - Deployment Architecture",
        filename=output_path("06_finova_deployment_architecture"),
        direction="LR",
        show=False,
        outformat="png",
        graph_attr={**graph_attr(compact=True), "size": "18,6!"},
    ):
        source = Git("Git repository")
        ci = CodePipeline("CodePipeline")
        acr = ContainerRegistry("ACR")
        ros = ResourceOrchestrationService("ROS")

        vpc = VirtualPrivateCloud("VPC template")
        frontend = ServerlessAppEngine("Frontend deployment")
        backend = ServerlessAppEngine("Backend deployment")
        worker = ElasticComputeService("Worker deployment")

        source >> ci >> acr
        source >> ros
        acr >> Edge(style="invis", weight="10") >> ros
        ros >> Edge(style="invis", weight="10") >> vpc
        vpc >> Edge(style="invis", weight="10") >> frontend
        frontend >> Edge(style="invis", weight="10") >> backend
        backend >> Edge(style="invis", weight="10") >> worker

        acr >> frontend
        acr >> backend
        acr >> worker
        ros >> vpc
        ros >> frontend
        ros >> backend
        ros >> worker
