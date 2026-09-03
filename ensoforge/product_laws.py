# Copyright (c) 2026 Martial Systems LLC
"""Refuse laws. Verify-before-done is the finish gate."""

from __future__ import annotations

from typing import Any


def laws() -> list[dict[str, Any]]:
    from ensoforge.graphs.claim_bans import build_graph as claim_bans
    from ensoforge.graphs.no_hydro import build_graph as no_hydro
    from ensoforge.graphs.pages import build_graph as pages
    from ensoforge.graphs.preseason import build_graph as preseason
    from ensoforge.graphs.temporal_split import build_graph as temporal_split
    from ensoforge.graphs.tmin_only import build_graph as tmin_only

    return [
        {
            "id": "enso.no_hydro",
            "build": no_hydro,
            "state": {
                "p_sfha_feature": False,
                "p_sfha_label": False,
                "hand_feature": False,
                "nora_q": False,
                "nwm_file": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "enso.tmin_only",
            "build": tmin_only,
            "state": {"tmin_only": True, "snow_as_tmin": False, "prcp_as_tmin": False},
            "allow_decisions": ["allow"],
        },
        {
            "id": "enso.preseason",
            "build": preseason,
            "state": {"same_year_october": False},
            "allow_decisions": ["allow"],
        },
        {
            "id": "enso.temporal_split",
            "build": temporal_split,
            "state": {
                "temporal_ok": True,
                "confirm_in_train": False,
                "confirm_in_median": False,
                "random_split": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "enso.claim_bans",
            "build": claim_bans,
            "state": {
                "frost_warning": False,
                "freeze_warning": False,
                "insurance": False,
                "will_freeze": False,
                "p_sfha": False,
                "hand_wet": False,
                "n_figures": 2,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "enso.pages",
            "build": pages,
            "state": {
                "page_in_scope": False,
                "ridge_beats_median": False,
                "readme_states_no": True,
            },
            "allow_decisions": ["allow"],
        },
    ]
