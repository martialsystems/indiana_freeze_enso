# Copyright (c) 2026 Martial Systems LLC

import pytest

from frzenso.errors import SplitError
from frzenso.split import CONFIRM, HOLDOUT, TRAIN, assert_split, role


def test_pinned_years() -> None:
    assert role("first_fall", 2018) == TRAIN
    assert role("last_spring", 2019) == TRAIN
    assert role("first_fall", 2019) == HOLDOUT
    assert role("last_spring", 2025) == HOLDOUT
    assert role("first_fall", 2025) == CONFIRM
    assert role("last_spring", 2026) == CONFIRM
    assert role("first_fall", 2024) == HOLDOUT
    assert role("last_spring", 2019) == TRAIN
    assert role("first_fall", 1991) == TRAIN
    assert role("last_spring", 1991) == TRAIN


def test_confirm_leak_refused() -> None:
    with pytest.raises(SplitError):
        assert_split(confirm_in_train=True, confirm_in_median=False, random_split=False)
    with pytest.raises(SplitError):
        assert_split(confirm_in_train=False, confirm_in_median=True, random_split=False)
    with pytest.raises(SplitError):
        assert_split(confirm_in_train=False, confirm_in_median=False, random_split=True)
