# Copyright (c) 2026 Martial Systems LLC
"""Median (train-era) vs last year vs October plus ENSO Ridge. MAE in days leads."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

import numpy as np

from frzenso.config import CLIMATE_FIRST, CLIMATE_LAST, COMPLETE_FRAC, CORE_IDS, TARGETS
from frzenso.dates import date_from_noleap_doy, error_days, iso, noleap_doy, yday
from frzenso.models import fit_ridge_per_target
from frzenso.pack import DatePack
from frzenso.split import CONFIRM, HOLDOUT, TRAIN, assert_split, role


def _keep(pack: DatePack) -> np.ndarray:
    return np.asarray(pack.complete_frac, dtype=float) >= COMPLETE_FRAC


def _median_dates(pack: DatePack, keep: np.ndarray) -> dict[tuple[str, str], date]:
    buckets: dict[tuple[str, str], list[int]] = defaultdict(list)
    for i in np.flatnonzero(keep):
        sid = str(pack.station_id[i])
        tgt = str(pack.target[i])
        year = int(pack.season_year[i])
        if role(tgt, year) != TRAIN:
            continue
        if year < CLIMATE_FIRST or year > CLIMATE_LAST:
            continue
        buckets[(sid, tgt)].append(noleap_doy(pack.obs_date[i]))
    return {k: date_from_noleap_doy(float(np.median(np.asarray(v, dtype=float)))) for k, v in buckets.items() if v}


def _lookup(pack: DatePack, keep: np.ndarray) -> dict[tuple[str, str, int], date]:
    return {
        (str(pack.station_id[i]), str(pack.target[i]), int(pack.season_year[i])): pack.obs_date[i]
        for i in np.flatnonzero(keep)
    }


def _stats(err: list[int]) -> dict[str, float]:
    a = np.asarray(err, dtype=float)
    if a.size == 0:
        return {"n": 0, "mae_days": float("nan"), "rmse_days": float("nan"), "bias_days": float("nan")}
    return {
        "n": int(a.size),
        "mae_days": float(np.mean(np.abs(a))),
        "rmse_days": float(np.sqrt(np.mean(a * a))),
        "bias_days": float(np.mean(a)),
    }


def score_pack(pack: DatePack) -> dict[str, Any]:
    keep = _keep(pack)
    medians = _median_dates(pack, keep)
    lookup = _lookup(pack, keep)
    assert_split(confirm_in_train=False, confirm_in_median=False, random_split=False)
    median_doy = np.array(
        [noleap_doy(medians[(str(pack.station_id[i]), str(pack.target[i]))]) if (str(pack.station_id[i]), str(pack.target[i])) in medians else np.nan for i in range(pack.n_rows)],
        dtype=float,
    )
    train = np.array([keep[i] and role(str(pack.target[i]), int(pack.season_year[i])) == TRAIN for i in range(pack.n_rows)])
    hold = np.array([keep[i] and role(str(pack.target[i]), int(pack.season_year[i])) == HOLDOUT for i in range(pack.n_rows)])
    conf = np.array([keep[i] and role(str(pack.target[i]), int(pack.season_year[i])) == CONFIRM for i in range(pack.n_rows)])
    fit = fit_ridge_per_target(pack, train=train, predict=hold | conf, median_doy=median_doy)

    def _rows(mask: np.ndarray, split: str) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for i in np.flatnonzero(mask):
            sid = str(pack.station_id[i])
            tgt = str(pack.target[i])
            year = int(pack.season_year[i])
            med = medians.get((sid, tgt))
            last = lookup.get((sid, tgt, year - 1))
            ridge_d = fit["pred_date"][i]
            if med is None or last is None or ridge_d is None:
                continue
            obs = pack.obs_date[i]
            out.append(
                {
                    "station_id": sid,
                    "name": str(pack.name[i]),
                    "lat": float(pack.lat[i]),
                    "lon": float(pack.lon[i]),
                    "target": tgt,
                    "season_year": year,
                    "split": split,
                    "obs": iso(obs),
                    "obs_yday": yday(obs),
                    "median": f"{med.month:02d}-{med.day:02d}",
                    "last_year": iso(last),
                    "ridge": f"{ridge_d.month:02d}-{ridge_d.day:02d}",
                    "err_median_days": int(error_days(med, obs)),
                    "err_last_year_days": int(error_days(last, obs)),
                    "err_ridge_days": int(error_days(ridge_d, obs)),
                    "_median_date": med,
                    "_last_date": last,
                    "_ridge_date": ridge_d,
                    "_obs_date": obs,
                }
            )
        return out

    hold_rows = _rows(hold, HOLDOUT)
    conf_rows = _rows(conf, CONFIRM)

    def _block(rows: list[dict[str, Any]]) -> dict[str, Any]:
        use = [x for x in rows if x["station_id"] in CORE_IDS]
        by_tgt: dict[str, dict[str, Any]] = {}
        for tgt in TARGETS:
            sub = [x for x in use if x["target"] == tgt]
            by_tgt[tgt] = {
                "median": _stats([x["err_median_days"] for x in sub]),
                "last_year": _stats([x["err_last_year_days"] for x in sub]),
                "ridge": _stats([x["err_ridge_days"] for x in sub]),
                "n": len(sub),
            }
        by_st: dict[str, dict[str, Any]] = {}
        for sid in sorted({x["station_id"] for x in use}):
            name = next(x["name"] for x in use if x["station_id"] == sid)
            cell: dict[str, Any] = {"name": name, "station_id": sid}
            for tgt in TARGETS:
                sub = [x for x in use if x["station_id"] == sid and x["target"] == tgt]
                cell[tgt] = {
                    "median": _stats([x["err_median_days"] for x in sub]),
                    "last_year": _stats([x["err_last_year_days"] for x in sub]),
                    "ridge": _stats([x["err_ridge_days"] for x in sub]),
                    "n": len(sub),
                }
            by_st[sid] = cell
        ridge_beats_both = all(
            by_tgt[t]["n"] and by_tgt[t]["ridge"]["mae_days"] < by_tgt[t]["median"]["mae_days"]
            for t in TARGETS
        )
        ridge_loses_both = all(
            by_tgt[t]["n"] and by_tgt[t]["ridge"]["mae_days"] >= by_tgt[t]["median"]["mae_days"]
            for t in TARGETS
        )
        return {
            "by_target": by_tgt,
            "by_station": by_st,
            "ridge_beats_both": ridge_beats_both,
            "ridge_loses_both": ridge_loses_both,
            "n": len(use),
        }

    cores = _block(hold_rows)
    return {
        "n_rows": pack.n_rows,
        "n_kept": int(keep.sum()),
        "n_train": int(train.sum()),
        "n_holdout": len(hold_rows),
        "n_confirm": len(conf_rows),
        "holdout_cores": cores,
        "confirm": _block(conf_rows) if conf_rows else None,
        "holdout_rows": hold_rows,
        "confirm_rows": conf_rows,
        "medians": {f"{k[0]}|{k[1]}": iso(v) for k, v in medians.items()},
        "ridge_coef": fit["coef"],
        "feature_names": list(fit["feature_names"]),
        "confirm_in_train": False,
        "confirm_in_median": False,
        "random_split": False,
        "ridge_beats_median": bool(cores["ridge_beats_both"]),
        "ridge_loses_both": bool(cores["ridge_loses_both"]),
        "page_in_scope": False,
        "units": "days",
        "threshold_f": 32.0,
        "parent_sha": "28941fb",
        "fall_holdout_years": list(range(2019, 2025)),
        "spring_holdout_years": list(range(2020, 2026)),
        "targets": list(TARGETS),
    }
