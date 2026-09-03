# Copyright (c) 2026 Martial Systems LLC
"""Ridge on prior-year October plus ENSO. One model per target. Not a deeper net if Ridge loses."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from frzenso.config import BANNED_FEATURE_TOKENS, FEATURE_NAMES, FIRST_FALL, LAST_SPRING
from frzenso.dates import date_from_noleap_doy, noleap_doy
from frzenso.errors import LeakError
from frzenso.pack import DatePack


def matrix_x(pack: DatePack, *, median_doy: np.ndarray) -> np.ndarray:
    names = " ".join(FEATURE_NAMES).lower()
    for tok in BANNED_FEATURE_TOKENS:
        if tok in names:
            raise LeakError(f"banned token {tok} in FEATURE_NAMES")
    x = np.column_stack(
        [
            np.asarray(pack.nino34_oct, dtype=float),
            np.asarray(median_doy, dtype=float),
            np.asarray(pack.oct_tavg_c, dtype=float),
            np.asarray(pack.oct_prcp_in, dtype=float),
            np.asarray(pack.lat, dtype=float),
            np.asarray(pack.elev_m, dtype=float),
        ]
    )
    if not np.isfinite(x).all():
        raise LeakError("non-finite feature")
    return x


def _clip_doy(tgt: str, doy: float) -> int:
    if tgt == FIRST_FALL:
        return int(min(365, max(244, round(doy))))
    if tgt == LAST_SPRING:
        return int(min(151, max(1, round(doy))))
    return int(round(doy))


def fit_ridge_per_target(
    pack: DatePack,
    *,
    train: np.ndarray,
    predict: np.ndarray,
    median_doy: np.ndarray,
) -> dict[str, Any]:
    x = matrix_x(pack, median_doy=median_doy)
    y = np.array([noleap_doy(d) for d in pack.obs_date.tolist()], dtype=float)
    pred = np.full(pack.n_rows, np.nan, dtype=float)
    models: dict[str, list[float]] = {}
    for tgt in (FIRST_FALL, LAST_SPRING):
        m_tr = train & (pack.target.astype(str) == tgt)
        m_pr = predict & (pack.target.astype(str) == tgt)
        if int(m_tr.sum()) < 8:
            continue
        pipe = Pipeline([("scale", StandardScaler()), ("reg", Ridge(alpha=1.0))])
        pipe.fit(x[m_tr], y[m_tr])
        if m_pr.any():
            raw = pipe.predict(x[m_pr])
            pred[m_pr] = np.array([_clip_doy(tgt, float(v)) for v in raw], dtype=float)
        coef = pipe.named_steps["reg"].coef_
        models[tgt] = [float(c) for c in coef]
    dates = np.empty(pack.n_rows, dtype=object)
    for i, doy in enumerate(pred):
        if np.isfinite(doy):
            dates[i] = date_from_noleap_doy(float(doy))
        else:
            dates[i] = None
    return {"pred_doy": pred, "pred_date": dates, "coef": models, "feature_names": list(FEATURE_NAMES)}
