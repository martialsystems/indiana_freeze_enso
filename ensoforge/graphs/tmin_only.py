# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from typing import Any

from ensoforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if not state.get("tmin_only"):
        v.append("not_tmin")
    if state.get("snow_as_tmin"):
        v.append("snow_as_tmin")
    if state.get("prcp_as_tmin"):
        v.append("prcp_as_tmin")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(name="enso.tmin_only", evaluate=_evaluate, extra=["tmin_only", "snow_as_tmin", "prcp_as_tmin"])
