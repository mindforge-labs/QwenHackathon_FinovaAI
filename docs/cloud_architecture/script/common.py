"""Shared helpers for Finova cloud architecture diagrams."""

from __future__ import annotations

from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
IMG_DIR = BASE_DIR / "img"

BASE_GRAPH_ATTR = {
    "fontsize": "26",
    "labelloc": "t",
    "pad": "0.55",
    "nodesep": "1.0",
    "ranksep": "1.2",
    "splines": "ortho",
    "dpi": "320",
}

README_GRAPH_ATTR = {
    **BASE_GRAPH_ATTR,
    "size": "16,9!",
}


def output_path(stem: str) -> str:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    return str((IMG_DIR / stem).resolve())


def graph_attr(*, compact: bool = False) -> dict[str, str]:
    attrs = dict(README_GRAPH_ATTR)
    if compact:
        attrs.update(
            {
                "nodesep": "0.85",
                "ranksep": "1.0",
                "pad": "0.45",
            }
        )
    return attrs
