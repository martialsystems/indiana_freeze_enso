# Copyright (c) 2026 Martial Systems LLC
"""Fail closed: October plus ENSO vs median date, not a warning."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from frzenso.errors import ClaimBanError

_BANS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("casualty", re.compile(r"\b(deaths?|fatalit(?:y|ies)|casualt(?:y|ies)|killed)\b", re.I)),
    ("frost_warning", re.compile(r"(?<!not a )\bfrost warning\b", re.I)),
    ("freeze_warning", re.compile(r"(?<!not a )\bfreeze warning\b", re.I)),
    ("frost_outlook", re.compile(r"\bfrost outlook\b", re.I)),
    ("insurance", re.compile(r"\b(?:crop |growing[- ]season )?insurance\b", re.I)),
    ("growing_season", re.compile(r"\bgrowing[- ]season\b", re.I)),
    ("cmip", re.compile(r"\b(cmip\d*|downscal(?:e|ed|ing)|gcm)\b", re.I)),
    ("climate_attr", re.compile(r"\bdue to climate change\b|\banthropogenic\b", re.I)),
    ("snow_proxy", re.compile(r"\bDJF snow\b.*\bproxy\b|\bsnow(?:fall)? inches as (?:a )?freeze\b", re.I)),
    ("p_sfha", re.compile(r"\bP\(sfha\b|\bp_sfha\b", re.I)),
    ("will_freeze", re.compile(r"Indiana will freeze on", re.I)),
    ("tornado", re.compile(r"\btornado\b", re.I)),
)


def scan_text(text: str) -> list[str]:
    hits = [name for name, pat in _BANS if pat.search(text or "")]
    if "\u2014" in (text or ""):
        hits.append("em_dash")
    return hits


def require_clean(text: str, *, source: str) -> None:
    hits = scan_text(text)
    if hits:
        raise ClaimBanError(f"{source}: banned claims {hits}")


def require_paths_clean(paths: Iterable[Path]) -> None:
    for path in paths:
        if path.is_file():
            require_clean(path.read_text(encoding="utf-8"), source=str(path))
