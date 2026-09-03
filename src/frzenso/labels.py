# Copyright (c) 2026 Martial Systems LLC
"""First/last 32 F from TMIN. October climate is the prior calendar year only."""

from __future__ import annotations

from datetime import date
from typing import Iterable

from frzenso.config import (
    COMPLETE_FRAC,
    FALL_END,
    FALL_START,
    FIRST_FALL,
    LAST_SPRING,
    SPRING_END,
    SPRING_START,
    THRESHOLD_F,
)

DailyTmin = list[tuple[date, float]]
DailyElem = list[tuple[date, str, float]]


def tmin_tenths_c_to_f(raw: float) -> float:
    return (float(raw) / 10.0) * 9.0 / 5.0 + 32.0


def window_bounds(target: str, year: int) -> tuple[date, date]:
    if target == FIRST_FALL:
        return date(year, *FALL_START), date(year, *FALL_END)
    if target == LAST_SPRING:
        return date(year, *SPRING_START), date(year, *SPRING_END)
    raise ValueError(f"unknown target {target}")


def _min_by_day(days: Iterable[tuple[date, float]]) -> dict[date, float]:
    out: dict[date, float] = {}
    for d, t in days:
        prev = out.get(d)
        out[d] = t if prev is None else min(prev, t)
    return out


def freeze_date(
    days: DailyTmin,
    *,
    target: str,
    year: int,
    floor: float = COMPLETE_FRAC,
    threshold_f: float = THRESHOLD_F,
) -> tuple[date | None, float, str]:
    start, end = window_bounds(target, year)
    expected = (end - start).days + 1
    by_day = _min_by_day((d, t) for d, t in days if start <= d <= end)
    frac = len(by_day) / float(expected) if expected else 0.0
    if frac < floor:
        return None, frac, "incomplete"
    hits = [d for d, t in sorted(by_day.items()) if t <= threshold_f]
    if not hits:
        return None, frac, "no_freeze_in_window"
    if target == FIRST_FALL:
        return hits[0], frac, "ok"
    return hits[-1], frac, "ok"


def october_climate(
    elems: DailyElem,
    *,
    oct_year: int,
    floor: float = COMPLETE_FRAC,
) -> tuple[float | None, float | None, float, str]:
    """October TAVG C and PRCP inches for calendar year oct_year. Not the freeze window."""
    start, end = date(oct_year, 10, 1), date(oct_year, 10, 31)
    tavg: dict[date, float] = {}
    tmax: dict[date, float] = {}
    tmin: dict[date, float] = {}
    prcp: dict[date, float] = {}
    for d, el, v in elems:
        if not (start <= d <= end):
            continue
        if el == "TAVG_C":
            tavg[d] = v
        elif el == "TMAX_C":
            tmax[d] = v
        elif el == "TMIN_C":
            tmin[d] = v
        elif el == "PRCP_IN":
            prcp[d] = v
    t_days = set(tavg)
    for d in set(tmax) & set(tmin):
        t_days.add(d)
        tavg.setdefault(d, 0.5 * (tmax[d] + tmin[d]))
    t_frac = len(t_days) / 31.0
    p_frac = len(prcp) / 31.0
    if t_frac < floor or p_frac < floor:
        return None, None, min(t_frac, p_frac), "incomplete"
    return float(sum(tavg[d] for d in t_days) / len(t_days)), float(sum(prcp.values())), min(t_frac, p_frac), "ok"


def season_years_in(days: DailyTmin, target: str) -> set[int]:
    years: set[int] = set()
    for d, _ in days:
        if target == FIRST_FALL and d.month >= FALL_START[0]:
            years.add(d.year)
        elif target == LAST_SPRING and d.month <= SPRING_END[0]:
            years.add(d.year)
    return years
