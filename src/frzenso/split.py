# Copyright (c) 2026 Martial Systems LLC
"""Temporal split. Same cut as indiana_freeze_date @28941fb. Confirmation out of the median."""

from __future__ import annotations

from frzenso.config import (
    FALL_CONFIRM_YEAR,
    FALL_HOLDOUT_YEARS,
    FALL_TRAIN_YEARS,
    FIRST_FALL,
    LAST_SPRING,
    SPRING_CONFIRM_YEAR,
    SPRING_HOLDOUT_YEARS,
    SPRING_TRAIN_YEARS,
)
from frzenso.errors import SplitError

TRAIN = "train"
HOLDOUT = "holdout"
CONFIRM = "confirm"
OTHER = "other"


def role(target: str, year: int) -> str:
    y = int(year)
    if target == FIRST_FALL:
        if y in FALL_TRAIN_YEARS:
            return TRAIN
        if y in FALL_HOLDOUT_YEARS:
            return HOLDOUT
        if y == FALL_CONFIRM_YEAR:
            return CONFIRM
        return OTHER
    if target == LAST_SPRING:
        if y in SPRING_TRAIN_YEARS:
            return TRAIN
        if y in SPRING_HOLDOUT_YEARS:
            return HOLDOUT
        if y == SPRING_CONFIRM_YEAR:
            return CONFIRM
        return OTHER
    raise SplitError(f"unknown target {target}")


def assert_split(*, confirm_in_train: bool, confirm_in_median: bool, random_split: bool) -> None:
    if confirm_in_train or confirm_in_median:
        raise SplitError("confirmation leaked into train or the median")
    if random_split:
        raise SplitError("random row split is refused")
