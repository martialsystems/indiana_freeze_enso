# Copyright (c) 2026 Martial Systems LLC
"""October features are prior-year only. Same-year October is inside first fall."""

from __future__ import annotations

from typing import Any

from ensoforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if state.get("same_year_october"):
        v.append("same_year_october")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(name="enso.preseason", evaluate=_evaluate, extra=["same_year_october"])
