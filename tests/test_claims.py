# Copyright (c) 2026 Martial Systems LLC

import pytest

from frzenso.claims import require_clean, scan_text
from frzenso.config import LIVE_BARS_SUBTITLE, LIVE_SCATTER_SUBTITLE, QUESTION
from frzenso.errors import ClaimBanError


def test_allowed_and_banned() -> None:
    assert scan_text(QUESTION) == []
    assert scan_text(LIVE_SCATTER_SUBTITLE) == []
    assert scan_text(LIVE_BARS_SUBTITLE) == []
    assert scan_text("first/last 32 °F date vs 1991-2020 median. MAE in days.") == []
    assert scan_text("days of error, not a frost warning.") == []
    assert scan_text("days of error, not a freeze warning.") == []
    assert "frost_warning" in scan_text("a frost warning is in effect")
    assert "freeze_warning" in scan_text("freeze warning tonight")
    assert "frost_outlook" in scan_text("public frost outlook")
    assert "will_freeze" in scan_text("Indiana will freeze on 2026-10-12")
    assert "p_sfha" in scan_text("p_sfha as a freeze date")
    assert "insurance" in scan_text("crop insurance")
    assert "growing_season" in scan_text("growing-season length")
    assert "cmip" in scan_text("CMIP6 downscaling")
    assert "snow_proxy" in scan_text("DJF snow as a freeze proxy")
    with pytest.raises(ClaimBanError):
        require_clean("crop insurance growing-season", source="t")
