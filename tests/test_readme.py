# Copyright (c) 2026 Martial Systems LLC

import json
from pathlib import Path

from frzenso.claims import scan_text
from frzenso.config import INDEX_GIST, QUESTION

REPO = Path(__file__).resolve().parents[1]
LIVE = REPO / "logs" / "in_live" / "stage_c_report.json"


def test_readme_opens_with_the_question() -> None:
    text = (REPO / "README.md").read_text(encoding="utf-8")
    body = "\n".join(text.splitlines()[1:]).lstrip()
    assert body.startswith(QUESTION)
    assert "1991-2020" in text
    assert "28941fb" in text
    assert "d861556" in text
    assert "USW00014848" in text
    assert "USW00014827" in text
    assert "USW00093819" in text
    assert "USW00093817" in text
    assert "Valparaiso" in text
    assert "not in this tree" in text.lower() or "not in the lead" in text.lower()
    assert "USW00004846" not in text.split("Valparaiso")[0]
    assert INDEX_GIST.split("/")[-1] in text
    assert "e5de316dbb5f672573906572730e3735" in text
    assert "scatter.png" in text
    assert "mae_bars.png" in text
    assert scan_text(text) == []
    assert "\u2014" not in text
    assert "What it is not" not in text
    assert "frost outlook" not in text.lower()
    assert "Indiana will freeze on" not in text
    assert "Research index: https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3" in text
    assert ".venv/bin/python -m pytest" in text
    assert "/usr/bin/python3 -m pytest" not in text
    assert "No on first fall" in text
    assert "yes on last spring" in text
    assert "9.96" in text
    assert "8.75" in text
    assert "7.62" in text
    assert "8.21" in text
    assert "11.67" in text
    assert "11.38" in text
    assert "Do not average" in text
    assert "Evansville" in text
    assert "South Bend" in text
    if LIVE.is_file():
        live = json.loads(LIVE.read_text(encoding="utf-8"))
        fall = live["holdout_cores"]["by_target"]["first_fall"]
        spring = live["holdout_cores"]["by_target"]["last_spring"]
        for block in (fall, spring):
            for key in ("median", "last_year", "ridge"):
                mae = block[key]["mae_days"]
                assert f"{mae:.2f}" in text or f"{mae:.1f}" in text
        assert live["ridge_beats_median"] is False
        assert live["ridge_loses_both"] is False
        assert not body[len(QUESTION) :].lstrip().lower().startswith("yes")
