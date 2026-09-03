# Copyright (c) 2026 Martial Systems LLC
"""GHCND TMIN for the label. October TAVG/PRCP are features. SNOW cannot substitute TMIN."""

from __future__ import annotations

import csv
import gzip
import io
from datetime import date
from pathlib import Path
from typing import Any, Callable

from frzenso.config import GHCND_STATION_URL, GHCND_STATIONS_URL, MM_PER_INCH
from frzenso.errors import FetchError
from frzenso.http import get_bytes
from frzenso.labels import tmin_tenths_c_to_f


def parse_station_line(line: str) -> dict[str, Any] | None:
    if len(line) < 41:
        return None
    sid = line[0:11].strip()
    try:
        lat = float(line[12:20])
        lon = float(line[21:30])
        elev = float(line[31:37])
    except ValueError:
        return None
    name = line[41:71].strip() if len(line) >= 71 else sid
    return {"station_id": sid, "lat": lat, "lon": lon, "elev_m": elev, "name": name}


def load_station_inventory(cache_dir: Path, getter: Callable[[str], bytes] = get_bytes) -> dict[str, dict[str, Any]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / "ghcnd-stations.txt"
    if not path.is_file() or path.stat().st_size == 0:
        path.write_bytes(getter(GHCND_STATIONS_URL))
    text = path.read_text(encoding="utf-8", errors="replace")
    out: dict[str, dict[str, Any]] = {}
    for line in text.splitlines():
        rec = parse_station_line(line)
        if rec:
            out[rec["station_id"]] = rec
    if not out:
        raise FetchError("empty GHCND station inventory")
    return out


def parse_station_csv(text: str) -> tuple[list[tuple[date, float]], list[tuple[date, str, float]]]:
    tmin: list[tuple[date, float]] = []
    elems: list[tuple[date, str, float]] = []
    for rec in csv.reader(io.StringIO(text)):
        if len(rec) < 4:
            continue
        el = rec[2].strip()
        qflag = rec[5].strip() if len(rec) > 5 else ""
        if qflag:
            continue
        try:
            raw = int(rec[3])
        except ValueError:
            continue
        if raw == -9999:
            continue
        day = date.fromisoformat(f"{rec[1][0:4]}-{rec[1][4:6]}-{rec[1][6:8]}")
        if el == "TMIN":
            tmin.append((day, tmin_tenths_c_to_f(raw)))
            elems.append((day, "TMIN_C", raw / 10.0))
        elif el == "TAVG":
            elems.append((day, "TAVG_C", raw / 10.0))
        elif el == "TMAX":
            elems.append((day, "TMAX_C", raw / 10.0))
        elif el == "PRCP":
            elems.append((day, "PRCP_IN", (raw / 10.0) / MM_PER_INCH))
    return tmin, elems


def load_station(sid: str, cache_dir: Path, getter: Callable[[str], bytes] = get_bytes) -> tuple[list[tuple[date, float]], list[tuple[date, str, float]]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{sid}.csv.gz"
    if not path.is_file() or path.stat().st_size == 0:
        body = getter(GHCND_STATION_URL.format(sid=sid))
        if not body:
            raise FetchError(f"empty GHCND {sid}")
        path.write_bytes(body)
    raw = gzip.decompress(path.read_bytes()).decode("utf-8", errors="replace")
    tmin, elems = parse_station_csv(raw)
    if not tmin:
        raise FetchError(f"GHCND {sid} has no TMIN")
    return tmin, elems
