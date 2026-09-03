# Copyright (c) 2026 Martial Systems LLC
"""Call sites for refuse laws."""

from __future__ import annotations

from typing import Any

from ensoforge._bootstrap import ensure_paths

ensure_paths()

from graphforge.product_law import require_law

from ensoforge.graphs.claim_bans import build_graph as build_claims
from ensoforge.graphs.no_hydro import build_graph as build_hydro
from ensoforge.graphs.pages import build_graph as build_pages
from ensoforge.graphs.preseason import build_graph as build_preseason
from ensoforge.graphs.temporal_split import build_graph as build_split
from ensoforge.graphs.tmin_only import build_graph as build_tmin


def require_no_hydro(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "enso_hydro"))
    state = {
        "p_sfha_feature": False,
        "p_sfha_label": False,
        "hand_feature": False,
        "nora_q": False,
        "nwm_file": False,
    }
    state.update(flags)
    require_law(build_hydro(), state, allow_decisions=["allow"], law_id="enso.no_hydro", thread_id=thread_id, raise_error=True)


def require_tmin(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "enso_tmin"))
    state = {"tmin_only": False, "snow_as_tmin": False, "prcp_as_tmin": False}
    state.update(flags)
    require_law(build_tmin(), state, allow_decisions=["allow"], law_id="enso.tmin_only", thread_id=thread_id, raise_error=True)


def require_preseason(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "enso_preseason"))
    state = {"same_year_october": False}
    state.update(flags)
    require_law(
        build_preseason(),
        state,
        allow_decisions=["allow"],
        law_id="enso.preseason",
        thread_id=thread_id,
        raise_error=True,
    )


def require_split(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "enso_split"))
    state = {
        "temporal_ok": True,
        "confirm_in_train": False,
        "confirm_in_median": False,
        "random_split": False,
    }
    state.update(flags)
    require_law(
        build_split(),
        state,
        allow_decisions=["allow"],
        law_id="enso.temporal_split",
        thread_id=thread_id,
        raise_error=True,
    )


def require_claims(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "enso_claims"))
    state = {
        "frost_warning": False,
        "freeze_warning": False,
        "insurance": False,
        "will_freeze": False,
        "p_sfha": False,
        "hand_wet": False,
        "n_figures": 2,
    }
    state.update(flags)
    require_law(
        build_claims(),
        state,
        allow_decisions=["allow"],
        law_id="enso.claim_bans",
        thread_id=thread_id,
        raise_error=True,
    )


def require_pages(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "enso_pages"))
    state = {
        "page_in_scope": False,
        "ridge_beats_median": False,
        "readme_states_no": False,
    }
    state.update(flags)
    require_law(build_pages(), state, allow_decisions=["allow"], law_id="enso.pages", thread_id=thread_id, raise_error=True)
