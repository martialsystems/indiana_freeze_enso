# Copyright (c) 2026 Martial Systems LLC
"""October plus ENSO vs 1991-2020 median first/last 32 F date. New tree, not a restamp of 28941fb."""

from __future__ import annotations

from pathlib import Path

QUESTION = (
    "Does October plus ENSO beat the 1991-2020 median first/last 32 °F date "
    "at held-out Indiana GHCND cores?"
)
USER_AGENT = "MartialSystemsResearch/indiana_freeze_enso"
MAX_FIGURES = 2
THRESHOLD_F = 32.0
COMPLETE_FRAC = 0.80
MM_PER_INCH = 25.4
INDEX_GIST = "https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3"
PARENT_SHA = "28941fb"
PARENT_REPO = "indiana_freeze_date"

CORE_STATIONS = (
    ("USW00014848", "South Bend"),
    ("USW00014827", "Fort Wayne"),
    ("USW00093819", "Indianapolis"),
    ("USW00093817", "Evansville"),
)
CORE_IDS = tuple(s for s, _ in CORE_STATIONS)

FALL_START = (9, 1)
FALL_END = (12, 31)
SPRING_START = (1, 1)
SPRING_END = (5, 31)
FIRST_FALL = "first_fall"
LAST_SPRING = "last_spring"
TARGETS = (FIRST_FALL, LAST_SPRING)

FALL_TRAIN_YEARS = tuple(range(1991, 2019))
SPRING_TRAIN_YEARS = tuple(range(1991, 2020))
FALL_HOLDOUT_YEARS = tuple(range(2019, 2025))
SPRING_HOLDOUT_YEARS = tuple(range(2020, 2026))
FALL_CONFIRM_YEAR = 2025
SPRING_CONFIRM_YEAR = 2026
CLIMATE_FIRST = 1991
CLIMATE_LAST = 2020
MIN_TRAIN_SEASONS = 20

# October of calendar year Y-1 is the pre-season vector for season year Y.
# Same-year October is inside the first-fall window and is refused.
FEATURE_NAMES = (
    "nino34_oct",
    "median_doy",
    "oct_tavg_c",
    "oct_prcp_in",
    "lat",
    "elev_m",
)
BANNED_FEATURE_TOKENS = ("tmin", "first_fall", "last_spring", "snow", "p_sfha", "hand", "nwm")

GHCND_STATION_URL = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_station/{sid}.csv.gz"
GHCND_STATIONS_URL = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
NINO_URL = "https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices"
REPO_ROOT = Path(__file__).resolve().parents[2]

LIVE_SCATTER_SUBTITLE = (
    "Holdout day-of-year. Median, last year, and October plus ENSO Ridge vs observed. "
    "Days of error, not a frost warning."
)
LIVE_BARS_SUBTITLE = "Holdout MAE in days. Median vs Ridge. Days of error, not a frost warning."
FIXTURE_SCATTER_SUBTITLE = "Fixture planted ENSO-date. Does not rescue live skill."
FIXTURE_BARS_SUBTITLE = "Fixture MAE in days. Does not rescue live skill."
