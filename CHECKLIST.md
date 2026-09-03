# Operator checklist

1. Fixture Stage 0 green. Planted ENSO-date so fixture Ridge beats the median. Fixture does not rescue live.
2. GHCND TMIN fetch-or-stop on the four cores. PRCP/SNOW cannot substitute. Empty core TMIN stops. CPC `sstoi.indices` fetch-or-stop.
3. Prior-year October only. Same-year October is refused. Last year is not a Ridge feature.
4. Train through fall 2018 / spring 2019. Holdout fall 2019-2024 and spring 2020-2025. Confirmation fall 2025 / spring 2026 out of the median.
5. Lead with MAE in days vs the median. Per-station table. Cite `28941fb` for last year as a bar. 7/24 is not the method. Live split: first fall 9.96 vs 8.75 (Ridge loses); last spring 7.62 vs 8.21 (Ridge wins). Do not average it.
6. Two figures. Pages stay off unless Ridge beats the median on both targets or the README states the no. Days of error, not a frost warning.
7. Do not edit freeze_date, DJF snow, NWM, Calumet, Pages, or HWM.
8. Research index: https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3 (Temp lane)
