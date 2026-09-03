# Copyright (c) 2026 Martial Systems LLC
"""Station-season freeze dates plus prior-year October climate."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

import numpy as np


@dataclass
class DatePack:
    station_id: np.ndarray
    name: np.ndarray
    lat: np.ndarray
    lon: np.ndarray
    elev_m: np.ndarray
    target: np.ndarray
    season_year: np.ndarray
    obs_date: np.ndarray
    complete_frac: np.ndarray
    nino34_oct: np.ndarray
    oct_tavg_c: np.ndarray
    oct_prcp_in: np.ndarray
    source: str = "fixture"
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def n_rows(self) -> int:
        return int(self.station_id.shape[0])

    @property
    def n_stations(self) -> int:
        return int(np.unique(self.station_id).shape[0])

    def dates(self) -> list[date]:
        return [d for d in self.obs_date.tolist()]
