# Copyright (c) 2026 Martial Systems LLC
"""Calendar helpers. Skill uses a 365-day year so last year is not a leap artifact."""

from __future__ import annotations

from datetime import date, timedelta


def noleap_doy(d: date) -> int:
    if d.month == 2 and d.day == 29:
        return 60
    return date(1999, d.month, d.day).timetuple().tm_yday


def date_from_noleap_doy(doy: float) -> date:
    n = int(round(float(doy)))
    n = min(365, max(1, n))
    return date(1999, 1, 1) + timedelta(days=n - 1)


def error_days(pred: date, obs: date) -> int:
    return noleap_doy(pred) - noleap_doy(obs)


def yday(d: date) -> int:
    return int(d.timetuple().tm_yday)


def iso(d: date) -> str:
    return d.isoformat()
