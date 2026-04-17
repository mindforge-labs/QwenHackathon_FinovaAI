"""North-south traffic path with edge security for Finova AI."""

from diagrams import Cluster, Diagram
from diagrams.alibabacloud.application import ApiGateway
from diagrams.alibabacloud.compute import ServerLoadBalancer, ServerlessAppEngine
from diagrams.alibabacloud.network import Cdn, EIP
from diagrams.alibabacloud.security import CloudFirewall, WebApplicationFirewall
from diagrams.alibabacloud.storage import ObjectStorageService
from diagrams.alibabacloud.web import Dns, Domain
from diagrams.onprem.client import User, Users
from diagrams.onprem.network import Internet

from common import graph_attr, output_path


def build_diagram() -> None:
    with Diagram(
        "Finova AI - Security Traffic Flow",
        filename=output_path("04_finova_security_traffic_flow"),
        direction="LR",
        show=False,
        outformat="png",
        graph_attr={**graph_attr(compact=True), "size": "18,5!"},
    ):
        borrowers = Users("Borrowers")
        reviewer = User("Reviewer")
        internet = Internet("Internet")
        domain = Domain("finova.example.com")
        dns = Dns("DNS")
        cdn = Cdn("CDN")
        waf = WebApplicationFirewall("WAF")
        firewall = CloudFirewall("Cloud Firewall")
        eip = EIP("Public entry")
        slb = ServerLoadBalancer("SLB")

        with Cluster("User-facing Runtime"):
            frontend = ServerlessAppEngine("Next.js frontend")
            gateway = ApiGateway("API Gateway")
            backend = ServerlessAppEngine("FastAPI API")
            oss = ObjectStorageService("OSS review assets")

        borrowers >> internet
        reviewer >> internet
        internet >> domain >> dns >> cdn >> waf >> firewall >> eip >> slb

        slb >> frontend
        slb >> gateway >> backend
        frontend >> gateway
        frontend >> oss
        backend >> oss
