# Copyright (c) 2026 Martial Systems LLC

from datetime import date, timedelta

from frzenso.config import FEATURE_NAMES
from frzenso.enso import parse_nino34_october
from frzenso.labels import freeze_date, october_climate, tmin_tenths_c_to_f


def test_32f_is_zero_c() -> None:
    assert tmin_tenths_c_to_f(0) == 32.0
    assert tmin_tenths_c_to_f(1) > 32.0
    assert tmin_tenths_c_to_f(-1) < 32.0


def test_first_fall_does_not_search_july() -> None:
    start = date(2018, 9, 1)
    filled = []
    for i in range(122):
        d = start + timedelta(days=i)
        filled.append((d, 31.0 if d == date(2018, 10, 12) else 50.0))
    filled.append((date(2018, 7, 4), 30.0))
    filled.append((date(2018, 8, 31), 31.0))
    obs, frac, reason = freeze_date(filled, target="first_fall", year=2018)
    assert reason == "ok"
    assert obs == date(2018, 10, 12)
    assert frac >= 0.80


def test_august_freeze_is_ignored() -> None:
    start = date(2018, 9, 1)
    filled = [(date(2018, 8, 20), 28.0)]
    for i in range(122):
        d = start + timedelta(days=i)
        filled.append((d, 31.0 if d == date(2018, 11, 1) else 50.0))
    obs, _, reason = freeze_date(filled, target="first_fall", year=2018)
    assert reason == "ok"
    assert obs == date(2018, 11, 1)


def test_last_spring_is_last_hit_on_or_before_31_may() -> None:
    filled = []
    start = date(2019, 1, 1)
    end = date(2019, 5, 31)
    n = (end - start).days + 1
    for i in range(n):
        d = start + timedelta(days=i)
        t = 28.0 if d in {date(2019, 3, 1), date(2019, 4, 15)} else 50.0
        filled.append((d, t))
    filled.append((date(2019, 6, 1), 28.0))
    obs, frac, reason = freeze_date(filled, target="last_spring", year=2019)
    assert reason == "ok"
    assert obs == date(2019, 4, 15)
    assert frac >= 0.80


def test_incomplete_window_drops() -> None:
    days = [(date(2018, 10, 1), 28.0)]
    obs, frac, reason = freeze_date(days, target="first_fall", year=2018)
    assert obs is None
    assert reason == "incomplete"
    assert frac < 0.80


def test_october_is_prior_calendar_year() -> None:
    elems = []
    for i in range(31):
        d = date(2017, 10, 1) + timedelta(days=i)
        elems.append((d, "TAVG_C", 12.0))
        elems.append((d, "PRCP_IN", 0.1))
    for i in range(31):
        d = date(2018, 10, 1) + timedelta(days=i)
        elems.append((d, "TAVG_C", 20.0))
        elems.append((d, "PRCP_IN", 1.0))
    tavg, prcp, frac, reason = october_climate(elems, oct_year=2017)
    assert reason == "ok"
    assert abs(float(tavg) - 12.0) < 1e-6
    assert abs(float(prcp) - 3.1) < 1e-6
    assert frac >= 0.80
    same_year, _, _, same_reason = october_climate(elems, oct_year=2018)
    assert same_reason == "ok"
    assert abs(float(same_year) - 20.0) < 1e-6
    blob = " ".join(FEATURE_NAMES).lower()
    assert "last_year" not in blob
    assert "last year" not in blob


def test_october_nino_maps_to_next_season_year() -> None:
    text = (
        "YR MON  NINO1+2   ANOM   NINO3    ANOM   NINO4    ANOM NINO3.4    ANOM\n"
        "2018  10   21.00    0.10   25.00    0.10   28.00    0.10   26.50    0.72\n"
        "2018   9   21.00    0.10   25.00    0.10   28.00    0.10   26.40    0.11\n"
    )
    out = parse_nino34_october(text)
    assert out[2019] == 0.72
    assert 2018 not in out
