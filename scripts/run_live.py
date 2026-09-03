#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
"""Live GHCND TMIN first/last 32 F vs median and October plus ENSO Ridge. Empty core TMIN stops."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "src")]

from frzenso.errors import FetchError  # noqa: E402
from frzenso.pipeline import run_live  # noqa: E402


def main() -> int:
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "logs" / "in_live"
    cache = Path(sys.argv[2]) if len(sys.argv) > 2 else REPO / "data" / "raw"
    try:
        report = run_live(dest, cache_dir=cache)
    except FetchError as exc:
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "fetch_stop.txt").write_text(str(exc) + "\n", encoding="utf-8")
        print(exc)
        return 2
    print(report["question"])
    cores = report["holdout_cores"]["by_target"]
    for tgt, block in cores.items():
        print(
            tgt,
            "median MAE",
            round(block["median"]["mae_days"], 2),
            "last year MAE",
            round(block["last_year"]["mae_days"], 2),
            "ridge MAE",
            round(block["ridge"]["mae_days"], 2),
        )
    print("ridge_beats_median", report["ridge_beats_median"])
    print("ridge_loses_both", report["ridge_loses_both"])
    print(report["figures"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
