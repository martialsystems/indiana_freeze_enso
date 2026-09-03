# Copyright (c) 2026 Martial Systems LLC
"""Two figures: holdout scatter, per-station MAE bars."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from frzenso.claims import require_clean
from frzenso.config import (
    CORE_STATIONS,
    FIRST_FALL,
    FIXTURE_BARS_SUBTITLE,
    FIXTURE_SCATTER_SUBTITLE,
    LAST_SPRING,
    LIVE_BARS_SUBTITLE,
    LIVE_SCATTER_SUBTITLE,
    MAX_FIGURES,
)
from frzenso.dates import noleap_doy
from frzenso.errors import FigureCapError

_TITLE = {FIRST_FALL: "First fall 32 F", LAST_SPRING: "Last spring 32 F"}


def _cap(n: int) -> None:
    if n > MAX_FIGURES:
        raise FigureCapError(f"this tree stops at {MAX_FIGURES} figures")


def write_scatter(dest: Path, *, fit: dict[str, Any], title: str, subtitle: str) -> Path:
    require_clean(title, source="fig1_title")
    require_clean(subtitle, source="fig1_sub")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = fit["holdout_rows"]
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.6))
    for ax, tgt in zip(axes, (FIRST_FALL, LAST_SPRING)):
        sub = [r for r in rows if r["target"] == tgt]
        obs = np.array([noleap_doy(r["_obs_date"]) for r in sub], dtype=float)
        med = np.array([noleap_doy(r["_median_date"]) for r in sub], dtype=float)
        ly = np.array([noleap_doy(r["_last_date"]) for r in sub], dtype=float)
        ridge = np.array([noleap_doy(r["_ridge_date"]) for r in sub], dtype=float)
        ax.scatter(obs, med, s=26, c="#64748b", marker="o", label="1991-2020 median", zorder=2)
        ax.scatter(obs, ly, s=22, c="#94a3b8", marker="x", label="last year", zorder=3)
        ax.scatter(obs, ridge, s=28, c="#b45309", marker="+", label="October plus ENSO", zorder=4)
        if obs.size:
            lo = float(np.nanmin([obs.min(), med.min(), ly.min(), ridge.min()]))
            hi = float(np.nanmax([obs.max(), med.max(), ly.max(), ridge.max()]))
        else:
            lo, hi = 1.0, 365.0
        pad = 0.05 * (hi - lo + 1.0)
        ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], color="#0f172a", lw=1.0, label="1:1")
        ax.set_xlabel("observed day-of-year")
        ax.set_ylabel("predicted day-of-year")
        ax.set_title(_TITLE[tgt], fontsize=10)
        ax.legend(fontsize=6, loc="upper left")
    fig.suptitle(title, fontsize=11)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.subplots_adjust(bottom=0.20, top=0.86, wspace=0.28)
    fig.text(0.5, 0.04, subtitle, ha="center", fontsize=8)
    fig.savefig(dest, dpi=130, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    return dest


def write_bars(dest: Path, *, fit: dict[str, Any], title: str, subtitle: str) -> Path:
    require_clean(title, source="fig2_title")
    require_clean(subtitle, source="fig2_sub")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    by_st = fit["holdout_cores"]["by_station"]
    order = [sid for sid, _ in CORE_STATIONS if sid in by_st]
    labels = [by_st[sid]["name"] for sid in order]
    x = np.arange(len(order), dtype=float)
    width = 0.25
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.6), sharey=True)
    for ax, tgt in zip(axes, (FIRST_FALL, LAST_SPRING)):
        med = [by_st[sid][tgt]["median"]["mae_days"] for sid in order]
        ridge = [by_st[sid][tgt]["ridge"]["mae_days"] for sid in order]
        ax.bar(x - width / 2, med, width, color="#64748b", label="1991-2020 median")
        ax.bar(x + width / 2, ridge, width, color="#b45309", label="October plus ENSO")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_title(_TITLE[tgt], fontsize=10)
        ax.set_ylabel("MAE (days)")
        ax.legend(fontsize=7, loc="upper right")
    fig.suptitle(title, fontsize=11)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.subplots_adjust(bottom=0.20, top=0.86, wspace=0.18)
    fig.text(0.5, 0.04, subtitle, ha="center", fontsize=8)
    fig.savefig(dest, dpi=130, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    return dest


def write_two(log_dir: Path, *, fit: dict[str, Any], live: bool) -> list[str]:
    _cap(2)
    log_dir.mkdir(parents=True, exist_ok=True)
    scatter = write_scatter(
        log_dir / "scatter.png",
        fit=fit,
        title="Holdout first/last 32 F dates",
        subtitle=LIVE_SCATTER_SUBTITLE if live else FIXTURE_SCATTER_SUBTITLE,
    )
    bars = write_bars(
        log_dir / "mae_bars.png",
        fit=fit,
        title="Per-station holdout MAE",
        subtitle=LIVE_BARS_SUBTITLE if live else FIXTURE_BARS_SUBTITLE,
    )
    paths = [scatter, bars]
    _cap(len(paths))
    return [p.name for p in paths]
