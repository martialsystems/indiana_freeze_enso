# Copyright (c) 2026 Martial Systems LLC
"""Live GHCND TMIN plus prior-year October climate. Empty core TMIN or Niño stops."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import numpy as np

from frzenso.config import CORE_IDS, CORE_STATIONS, MIN_TRAIN_SEASONS, TARGETS
from frzenso.enso import load_nino34
from frzenso.errors import FetchError
from frzenso.ghcnd import load_station, load_station_inventory
from frzenso.http import get_bytes
from frzenso.labels import freeze_date, october_climate, season_years_in
from frzenso.pack import DatePack
from frzenso.split import TRAIN, role


def fetch_live(*, cache_dir: Path, getter: Callable[[str], bytes] = get_bytes) -> tuple[DatePack, dict[str, Any]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    inventory = load_station_inventory(cache_dir, getter=getter)
    nino = load_nino34(cache_dir, getter=getter)
    rows: list[dict[str, Any]] = []
    holes: list[dict[str, Any]] = []
    for sid, fallback in CORE_STATIONS:
        try:
            tmin, elems = load_station(sid, cache_dir, getter=getter)
        except FetchError:
            raise FetchError(f"empty GHCND TMIN for required core {sid}") from None
        rec = inventory.get(sid) or {}
        name = rec.get("name") or fallback
        lat = float(rec.get("lat") or 0.0)
        lon = float(rec.get("lon") or 0.0)
        elev = float(rec.get("elev_m") or 0.0)
        hole: dict[str, Any] = {"station_id": sid, "incomplete": [], "no_freeze": [], "oct_miss": [], "nino_miss": []}
        for target in TARGETS:
            for year in sorted(season_years_in(tmin, target)):
                obs, frac, reason = freeze_date(tmin, target=target, year=int(year))
                if reason == "incomplete":
                    hole["incomplete"].append({"target": target, "year": int(year), "complete_frac": frac})
                    continue
                if reason == "no_freeze_in_window":
                    hole["no_freeze"].append({"target": target, "year": int(year)})
                    continue
                if int(year) not in nino:
                    hole["nino_miss"].append({"target": target, "year": int(year)})
                    continue
                tavg, prcp, ofrac, oreason = october_climate(elems, oct_year=int(year) - 1)
                if oreason != "ok":
                    hole["oct_miss"].append({"target": target, "year": int(year), "oct_year": int(year) - 1})
                    continue
                rows.append(
                    {
                        "station_id": sid,
                        "name": name,
                        "lat": lat,
                        "lon": lon,
                        "elev_m": elev,
                        "target": target,
                        "season_year": int(year),
                        "obs_date": obs,
                        "complete_frac": float(frac),
                        "nino34_oct": float(nino[int(year)]),
                        "oct_tavg_c": float(tavg),
                        "oct_prcp_in": float(prcp),
                    }
                )
        holes.append(hole)
        train_n = {t: 0 for t in TARGETS}
        for r in rows:
            if r["station_id"] == sid and role(r["target"], r["season_year"]) == TRAIN:
                train_n[r["target"]] += 1
        if train_n[TARGETS[0]] < MIN_TRAIN_SEASONS or train_n[TARGETS[1]] < MIN_TRAIN_SEASONS:
            raise FetchError(f"core {sid} too thin for median: train n={train_n}")
    missing = set(CORE_IDS) - {r["station_id"] for r in rows}
    if missing:
        raise FetchError(f"required cores missing after QC: {sorted(missing)}")
    pack = DatePack(
        station_id=np.array([r["station_id"] for r in rows], dtype=object),
        name=np.array([r["name"] for r in rows], dtype=object),
        lat=np.array([r["lat"] for r in rows], dtype=float),
        lon=np.array([r["lon"] for r in rows], dtype=float),
        elev_m=np.array([r["elev_m"] for r in rows], dtype=float),
        target=np.array([r["target"] for r in rows], dtype=object),
        season_year=np.array([r["season_year"] for r in rows], dtype=int),
        obs_date=np.array([r["obs_date"] for r in rows], dtype=object),
        complete_frac=np.array([r["complete_frac"] for r in rows], dtype=float),
        nino34_oct=np.array([r["nino34_oct"] for r in rows], dtype=float),
        oct_tavg_c=np.array([r["oct_tavg_c"] for r in rows], dtype=float),
        oct_prcp_in=np.array([r["oct_prcp_in"] for r in rows], dtype=float),
        source="live",
        extra={"element": "TMIN", "feature_october": "prior_year", "holes": holes},
    )
    meta = {
        "n_stations": pack.n_stations,
        "n_rows": pack.n_rows,
        "product": "GHCND TMIN + prior-year October + Niño 3.4",
        "units": "F",
        "threshold_f": 32.0,
        "parent_sha": "28941fb",
        "cache_dir": str(cache_dir),
        "holes": holes,
    }
    return pack, meta
