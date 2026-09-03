# Copyright (c) 2026 Martial Systems LLC

import json
from pathlib import Path

from frzenso.config import QUESTION
from frzenso.errors import FigureCapError
from frzenso.figure import _cap
from frzenso.pipeline import stage0_fixture

LIVE = Path(__file__).resolve().parents[1] / "logs" / "in_live" / "stage_c_report.json"


def test_fixture_two_figures(tmp_path: Path) -> None:
    report = stage0_fixture(tmp_path)
    assert report["question"] == QUESTION
    assert report["figures"] == ["scatter.png", "mae_bars.png"]
    assert (tmp_path / "scatter.png").is_file()
    assert (tmp_path / "mae_bars.png").is_file()
    assert report["p_sfha_feature"] is False
    assert report["nwm_file"] is False
    assert report["snow_as_tmin"] is False
    assert report["same_year_october"] is False
    assert report["page_in_scope"] is False
    assert report["element"] == "TMIN"
    assert report["feature_october"] == "prior_year"
    assert report["parent_sha"] == "28941fb"
    cores = report["holdout_cores"]["by_station"]
    assert "USW00014848" in cores
    assert "USW00093817" in cores
    assert "USW00004846" not in cores
    by_tgt = report["holdout_cores"]["by_target"]
    assert by_tgt["first_fall"]["n"] > 0
    assert by_tgt["last_spring"]["n"] > 0
    assert by_tgt["first_fall"]["ridge"]["mae_days"] < by_tgt["first_fall"]["median"]["mae_days"]
    assert by_tgt["last_spring"]["ridge"]["mae_days"] < by_tgt["last_spring"]["median"]["mae_days"]
    assert report["ridge_beats_median"] is True
    assert report["confirm_in_train"] is False
    assert report["confirm_in_median"] is False
    assert report["fall_holdout_years"] == [2019, 2020, 2021, 2022, 2023, 2024]
    assert report["spring_holdout_years"] == [2020, 2021, 2022, 2023, 2024, 2025]


def test_live_holdout_keeps_page_closed() -> None:
    if not LIVE.is_file():
        return
    live = json.loads(LIVE.read_text(encoding="utf-8"))
    assert live["page_in_scope"] is False
    assert live["element"] == "TMIN"
    assert live["feature_october"] == "prior_year"
    assert live["same_year_october"] is False
    assert "USW00004846" not in live["holdout_cores"]["by_station"]
    fall = live["holdout_cores"]["by_target"]["first_fall"]
    spring = live["holdout_cores"]["by_target"]["last_spring"]
    assert fall["n"] == 24
    assert spring["n"] == 24
    assert live["ridge_beats_median"] is False
    assert live["ridge_loses_both"] is False
    assert fall["ridge"]["mae_days"] > fall["median"]["mae_days"]
    assert spring["ridge"]["mae_days"] < spring["median"]["mae_days"]
    assert live["confirm_in_median"] is False
    assert live["parent_sha"] == "28941fb"


def test_third_figure_refused() -> None:
    try:
        _cap(3)
        raise AssertionError("cap allowed 3")
    except FigureCapError:
        pass
