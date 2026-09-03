# Copyright (c) 2026 Martial Systems LLC

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from ensoforge._bootstrap import ensure_paths

ensure_paths()

from graphforge.product_law import LawBlockedError

from ensoforge.gate import (
    require_claims,
    require_no_hydro,
    require_pages,
    require_preseason,
    require_split,
    require_tmin,
)
from ensoforge.product_laws import laws


def test_laws() -> None:
    require_no_hydro(thread_id="t.h.ok")
    with pytest.raises(LawBlockedError):
        require_no_hydro(p_sfha_feature=True, thread_id="t.h.p")
    with pytest.raises(LawBlockedError):
        require_no_hydro(nwm_file=True, thread_id="t.h.nwm")
    require_tmin(tmin_only=True, thread_id="t.t.ok")
    with pytest.raises(LawBlockedError):
        require_tmin(tmin_only=True, snow_as_tmin=True, thread_id="t.t.snow")
    require_preseason(same_year_october=False, thread_id="t.pre.ok")
    with pytest.raises(LawBlockedError):
        require_preseason(same_year_october=True, thread_id="t.pre.same")
    require_split(thread_id="t.s.ok")
    with pytest.raises(LawBlockedError):
        require_split(confirm_in_median=True, thread_id="t.s.med")
    require_claims(n_figures=2, thread_id="t.k.ok")
    with pytest.raises(LawBlockedError):
        require_claims(n_figures=3, thread_id="t.k.fig")
    require_pages(page_in_scope=False, readme_states_no=True, thread_id="t.p.ok")
    with pytest.raises(LawBlockedError):
        require_pages(page_in_scope=True, ridge_beats_median=False, readme_states_no=False, thread_id="t.p.bad")
    require_pages(page_in_scope=True, ridge_beats_median=True, readme_states_no=False, thread_id="t.p.win")
    assert {row["id"] for row in laws()} == {
        "enso.no_hydro",
        "enso.tmin_only",
        "enso.preseason",
        "enso.temporal_split",
        "enso.claim_bans",
        "enso.pages",
    }
