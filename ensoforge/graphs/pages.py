# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from typing import Any

from ensoforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if state.get("page_in_scope") and not state.get("ridge_beats_median"):
        if not state.get("readme_states_no"):
            v.append("page_without_skill")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="enso.pages",
        evaluate=_evaluate,
        extra=["page_in_scope", "ridge_beats_median", "readme_states_no"],
    )
