# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from typing import Any

from ensoforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if not state.get("temporal_ok"):
        v.append("not_temporal")
    if state.get("confirm_in_train"):
        v.append("confirm_in_train")
    if state.get("confirm_in_median"):
        v.append("confirm_in_median")
    if state.get("random_split"):
        v.append("random_split")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="enso.temporal_split",
        evaluate=_evaluate,
        extra=["temporal_ok", "confirm_in_train", "confirm_in_median", "random_split"],
    )
