# Copyright (c) 2026 Martial Systems LLC
"""CPC ERSST Niño 3.4. October of year Y-1 is the pre-season value for season year Y."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from frzenso.config import NINO_URL
from frzenso.errors import FetchError
from frzenso.http import get_bytes


def parse_nino34_october(text: str) -> dict[int, float]:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        raise FetchError("empty Niño 3.4 file")
    header = lines[0].upper()
    if "NINO3.4" not in header.replace(" ", ""):
        raise FetchError("Niño 3.4 column missing")
    out: dict[int, float] = {}
    for ln in lines[1:]:
        parts = ln.split()
        if len(parts) < 10:
            continue
        try:
            year = int(parts[0])
            month = int(parts[1])
            nino = float(parts[9])
        except ValueError:
            continue
        if month != 10:
            continue
        out[year + 1] = nino
    if not out:
        raise FetchError("no October Niño 3.4 rows")
    return out


def load_nino34(cache_dir: Path, getter: Callable[[str], bytes] = get_bytes) -> dict[int, float]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / "sstoi.indices"
    if not path.is_file() or path.stat().st_size == 0:
        body = getter(NINO_URL)
        if not body:
            raise FetchError("empty Niño 3.4 fetch")
        path.write_bytes(body)
    return parse_nino34_october(path.read_text(encoding="utf-8", errors="replace"))
