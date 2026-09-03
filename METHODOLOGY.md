# Methodology: October plus ENSO vs 1991-2020 median first/last 32 °F date

Question: Does October plus ENSO beat the 1991-2020 median first/last 32 °F date at held-out Indiana GHCND cores?

This is a new label/model tree. Parent last-year vs median is frozen at `28941fb` in `indiana_freeze_date`. Last year is a bar here, not the question and not a Ridge feature.

## Label

GHCND `TMIN` in °F. 32 °F is the lock.

| Target | Rule | Season year |
|--------|------|-------------|
| First fall 32 °F | First day with TMIN ≤ 32 °F on or after 1 Sep, through 31 Dec | year of that Sep |
| Last spring 32 °F | Last day with TMIN ≤ 32 °F on or before 31 May, from 1 Jan | year of that May |

July is not searched for a first freeze. Missing TMIN: drop that station-season if completeness is under 80% of days in the window. No freeze in the window is also a drop. Empty TMIN for a required core stops.

Skill uses day-of-year on a 365-day calendar so last year is not a leap artifact. Printed dates are the real calendar dates.

## Stations

Required cores: South Bend `USW00014848`, Fort Wayne `USW00014827`, Indianapolis `USW00093819`, Evansville `USW00093817`.

Valparaiso is not in this tree.

## Features

October of the prior calendar year only: Niño 3.4 (CPC ERSST `sstoi.indices`), station October mean temperature (°C), station October precipitation (inches), plus the train-era median day-of-year, latitude, and elevation.

Same-year October sits inside the first-fall window and is refused (`same_year_october=False`). Last year's freeze date is a scored bar, not a Ridge column.

## Bars

Bar A: 1991-2020 median first/last date at that station, computed on train-era seasons only (fall 1991-2018, spring 1991-2019). Holdout and confirmation do not set the median.

Bar B: last year's date at that station (cite `28941fb`; not this tree's question). A holdout row is scored only when last year is also complete.

Bar C: Ridge per target. `StandardScaler` plus `Ridge(alpha=1)`. One model per target.

## Split

Rows: station × season × target. Identical to `indiana_freeze_date` @ `28941fb`.

Train: fall 1991-2018 and spring 1991-2019.

Holdout: fall 2019, 2020, 2021, 2022, 2023, 2024 and spring 2020, 2021, 2022, 2023, 2024, 2025.

Confirmation: fall 2025 and spring 2026, out of train and out of the median.

## Metrics

Lead with MAE in days vs the median. RMSE second. Per-station table required. A 7/24 count is not the method. If Ridge wins only one target, say that; do not average it away.

## Figures

1. Holdout scatter: predicted vs observed day-of-year, 1:1, first-fall and last-spring as two panels.
2. Per-station MAE bars: median vs Ridge. Caption: days of error, not a frost warning.

Two figures max.

## Fixture

Synthetic dates at the four cores with a planted ENSO-date link. Fixture Ridge is required to beat the median. That does not rescue live skill.

## Pages

A public date hero is refused unless Ridge beats the median on both targets, or the README states the no.

## Live lock

Holdout n=24 per target on the four cores. Ridge does not beat both targets. First fall MAE 9.96 vs median 8.75. Last spring MAE 7.62 vs median 8.21. Last year 11.67 / 11.38 matches `28941fb` and is not the question. Evansville Ridge beats the median on both targets. South Bend Ridge loses both. Confirmation fall 2025 / spring 2026 does not set the median and does not reopen a page. Valparaiso is not in this tree.
