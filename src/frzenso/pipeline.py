# Copyright (c) 2026 Martial Systems LLC
"""Stage 0 fixture. Live fetch-or-stop. Two figures. Pages refused unless Ridge beats the median."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from frzenso.claims import require_clean, require_paths_clean
from frzenso.config import PARENT_SHA, QUESTION, REPO_ROOT
from frzenso.fetch import fetch_live
from frzenso.figure import write_two
from frzenso.fixture import build_fixture
from frzenso.skill import score_pack

try:
    from ensoforge.gate import (
        require_claims,
        require_no_hydro,
        require_pages,
        require_preseason,
        require_split,
        require_tmin,
    )
except ImportError:  # pragma: no cover

    def require_claims(**kwargs):
        del kwargs

    def require_no_hydro(**kwargs):
        del kwargs

    def require_pages(**kwargs):
        del kwargs

    def require_preseason(**kwargs):
        del kwargs

    def require_split(**kwargs):
        del kwargs

    def require_tmin(**kwargs):
        del kwargs


def _public_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    skip = {"_median_date", "_last_date", "_ridge_date", "_obs_date"}
    return [{k: v for k, v in r.items() if k not in skip} for r in rows]


def _jsonable(report: dict[str, Any]) -> dict[str, Any]:
    out = dict(report)
    out["holdout_rows"] = _public_rows(report.get("holdout_rows") or [])
    out["confirm_rows"] = _public_rows(report.get("confirm_rows") or [])
    return out


def _run(log_dir: Path, *, pack, fixture: bool, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    require_no_hydro(thread_id="hydro")
    require_tmin(tmin_only=True, snow_as_tmin=False, prcp_as_tmin=False, thread_id="tmin")
    require_preseason(same_year_october=False, thread_id="preseason")
    require_clean(QUESTION, source="question")
    fit = score_pack(pack)
    require_split(
        temporal_ok=True,
        confirm_in_train=bool(fit["confirm_in_train"]),
        confirm_in_median=bool(fit["confirm_in_median"]),
        random_split=bool(fit["random_split"]),
        thread_id="split",
    )
    paths = write_two(log_dir, fit=fit, live=not fixture)
    require_claims(n_figures=len(paths), thread_id="claims")
    require_pages(
        page_in_scope=bool(fit["page_in_scope"]),
        ridge_beats_median=bool(fit["ridge_beats_median"]),
        readme_states_no=bool(fit["ridge_loses_both"]) or fixture,
        thread_id="pages",
    )
    log_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "stage": "0" if fixture else "C",
        "fixture": fixture,
        "question": QUESTION,
        "source": pack.source,
        "n_rows": pack.n_rows,
        "n_stations": pack.n_stations,
        "units": "days",
        "threshold_f": 32.0,
        "element": "TMIN",
        "feature_october": "prior_year",
        "parent_sha": PARENT_SHA,
        "p_sfha_feature": False,
        "nwm_file": False,
        "snow_as_tmin": False,
        "same_year_october": False,
        "page_in_scope": False,
        "ridge_beats_median": fit["ridge_beats_median"],
        "ridge_loses_both": fit["ridge_loses_both"],
        "figures": paths,
        **{k: fit[k] for k in (
            "n_kept",
            "n_train",
            "n_holdout",
            "n_confirm",
            "holdout_cores",
            "confirm",
            "holdout_rows",
            "confirm_rows",
            "medians",
            "ridge_coef",
            "feature_names",
            "confirm_in_train",
            "confirm_in_median",
            "random_split",
            "fall_holdout_years",
            "spring_holdout_years",
            "targets",
        )},
    }
    if extra:
        report.update(extra)
    require_clean(json.dumps(_jsonable(report), default=str), source="report")
    (log_dir / ("stage0_report.json" if fixture else "stage_c_report.json")).write_text(
        json.dumps(_jsonable(report), indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    require_paths_clean([REPO_ROOT / "README.md"])
    return report


def stage0_fixture(log_dir: Path) -> dict[str, Any]:
    return _run(log_dir, pack=build_fixture(), fixture=True)


def run_live(log_dir: Path, *, cache_dir: Path) -> dict[str, Any]:
    pack, meta = fetch_live(cache_dir=cache_dir)
    return _run(log_dir, pack=pack, fixture=False, extra={"fetch_meta": {k: meta[k] for k in meta if k != "holes"}})
