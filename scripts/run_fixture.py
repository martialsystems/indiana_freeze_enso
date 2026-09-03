#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "src")]

from frzenso.pipeline import stage0_fixture  # noqa: E402


def main() -> int:
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "logs" / "stage0_fixture"
    report = stage0_fixture(dest)
    print(report["question"])
    cores = report["holdout_cores"]["by_target"]
    for tgt, block in cores.items():
        print(
            tgt,
            "median MAE",
            block["median"]["mae_days"],
            "last year MAE",
            block["last_year"]["mae_days"],
            "ridge MAE",
            block["ridge"]["mae_days"],
        )
    print("ridge_beats_median", report["ridge_beats_median"])
    print(report["figures"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
