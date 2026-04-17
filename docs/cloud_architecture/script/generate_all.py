"""Render the full Finova Alibaba Cloud architecture diagram set."""

from __future__ import annotations

from pathlib import Path
import sys


CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from importlib import import_module


build_overview = import_module("01_finova_cloud_overview").build_diagram
build_async_processing = import_module("02_finova_async_processing_architecture").build_diagram
build_data_storage = import_module("03_finova_data_storage_architecture").build_diagram
build_security_traffic = import_module("04_finova_security_traffic_flow").build_diagram
build_security = import_module("05_finova_security_architecture").build_diagram
build_deployment = import_module("06_finova_deployment_architecture").build_diagram


def main() -> None:
    build_overview()
    build_async_processing()
    build_data_storage()
    build_security_traffic()
    build_security()
    build_deployment()


if __name__ == "__main__":
    main()
