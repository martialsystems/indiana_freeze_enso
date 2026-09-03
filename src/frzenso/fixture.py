# Copyright (c) 2026 Martial Systems LLC
"""Synthetic dates with a planted ENSO-date link. Does not rescue live skill."""

from __future__ import annotations

import numpy as np

from frzenso.config import (
    CORE_STATIONS,
    FALL_CONFIRM_YEAR,
    FIRST_FALL,
    LAST_SPRING,
    SPRING_CONFIRM_YEAR,
)
from frzenso.dates import date_from_noleap_doy
from frzenso.pack import DatePack

_COORDS = {
    "USW00014848": (41.71, -86.32, 236.0, "South Bend"),
    "USW00014827": (41.12, -85.19, 248.0, "Fort Wayne"),
    "USW00093819": (39.72, -86.29, 241.0, "Indianapolis"),
    "USW00093817": (38.04, -87.53, 118.0, "Evansville"),
}
_FALL_MEAN = {"USW00014848": 278, "USW00014827": 283, "USW00093819": 291, "USW00093817": 301}
_SPRING_MEAN = {"USW00014848": 115, "USW00014827": 110, "USW00093819": 102, "USW00093817": 87}


def build_fixture(*, seed: int = 11) -> DatePack:
    rng = np.random.default_rng(seed)
    fall_years = list(range(1991, FALL_CONFIRM_YEAR + 1))
    spring_years = list(range(1991, SPRING_CONFIRM_YEAR + 1))
    nino_map = {int(y): float(rng.normal(0.0, 0.9)) for y in range(1990, SPRING_CONFIRM_YEAR + 1)}
    rows: dict[str, list] = {k: [] for k in (
        "station_id", "name", "lat", "lon", "elev_m", "target", "season_year",
        "obs_date", "complete_frac", "nino34_oct", "oct_tavg_c", "oct_prcp_in",
    )}
    for sid, _ in CORE_STATIONS:
        lat, lon, elev, name = _COORDS[sid]
        for y in fall_years:
            n34 = nino_map[int(y)]
            # Warm Niño → later first freeze (higher DOY).
            doy = int(min(340, max(250, round(_FALL_MEAN[sid] + 8.0 * n34 + rng.normal(0.0, 2.5)))))
            rows["station_id"].append(sid)
            rows["name"].append(name)
            rows["lat"].append(lat)
            rows["lon"].append(lon)
            rows["elev_m"].append(elev)
            rows["target"].append(FIRST_FALL)
            rows["season_year"].append(int(y))
            rows["obs_date"].append(date_from_noleap_doy(doy).replace(year=int(y)))
            rows["complete_frac"].append(0.95)
            rows["nino34_oct"].append(n34)
            rows["oct_tavg_c"].append(10.0 + 1.2 * n34 + rng.normal(0.0, 0.4))
            rows["oct_prcp_in"].append(max(0.2, 3.0 + rng.normal(0.0, 0.5)))
        for y in spring_years:
            n34 = nino_map[int(y)]
            # Warm Niño → earlier last spring freeze (lower DOY).
            doy = int(min(140, max(50, round(_SPRING_MEAN[sid] - 7.0 * n34 + rng.normal(0.0, 2.5)))))
            rows["station_id"].append(sid)
            rows["name"].append(name)
            rows["lat"].append(lat)
            rows["lon"].append(lon)
            rows["elev_m"].append(elev)
            rows["target"].append(LAST_SPRING)
            rows["season_year"].append(int(y))
            rows["obs_date"].append(date_from_noleap_doy(doy).replace(year=int(y)))
            rows["complete_frac"].append(0.95)
            rows["nino34_oct"].append(n34)
            rows["oct_tavg_c"].append(10.0 + 1.2 * n34 + rng.normal(0.0, 0.4))
            rows["oct_prcp_in"].append(max(0.2, 3.0 + rng.normal(0.0, 0.5)))
    return DatePack(
        station_id=np.array(rows["station_id"], dtype=object),
        name=np.array(rows["name"], dtype=object),
        lat=np.array(rows["lat"], dtype=float),
        lon=np.array(rows["lon"], dtype=float),
        elev_m=np.array(rows["elev_m"], dtype=float),
        target=np.array(rows["target"], dtype=object),
        season_year=np.array(rows["season_year"], dtype=int),
        obs_date=np.array(rows["obs_date"], dtype=object),
        complete_frac=np.array(rows["complete_frac"], dtype=float),
        nino34_oct=np.array(rows["nino34_oct"], dtype=float),
        oct_tavg_c=np.array(rows["oct_tavg_c"], dtype=float),
        oct_prcp_in=np.array(rows["oct_prcp_in"], dtype=float),
        source="fixture",
        extra={"planted_enso": True},
    )
