# Copyright (c) 2026 Martial Systems LLC

import gzip
from datetime import date
from pathlib import Path

import pytest

from frzenso.errors import FetchError
from frzenso.fetch import fetch_live
from frzenso.ghcnd import parse_station_csv
from frzenso.labels import tmin_tenths_c_to_f


def test_parse_tmin_ignores_snow_and_prcp() -> None:
    text = (
        "USW00014848,20181012,SNOW,25,,,\n"
        "USW00014848,20181012,PRCP,10,,,\n"
        "USW00014848,20181012,TMIN,0,,,\n"
        "USW00014848,20181012,TMIN,-9999,,,\n"
    )
    tmin, elems = parse_station_csv(text)
    assert tmin == [(date(2018, 10, 12), 32.0)]
    assert tmin_tenths_c_to_f(0) == 32.0
    assert all(el != "SNOW" for _, el, _ in elems)


def _gz(lines: list[str]) -> bytes:
    return gzip.compress("\n".join(lines).encode("utf-8"))


def _nino() -> bytes:
    return (
        "YR MON  NINO1+2   ANOM   NINO3    ANOM   NINO4    ANOM NINO3.4    ANOM\n"
        "2017  10   21.00    0.10   25.00    0.10   28.00    0.10   26.50    0.72\n"
    ).encode()


def test_empty_core_tmin_stops(tmp_path: Path) -> None:
    def getter(url: str) -> bytes:
        if url.endswith("ghcnd-stations.txt"):
            return (
                "USW00014848  41.7100  -86.3200  236.0 SOUTH BEND          IN US\n"
                "USW00014827  41.1200  -85.1900  248.0 FORT WAYNE         IN US\n"
                "USW00093819  39.7200  -86.2900  241.0 INDIANAPOLIS       IN US\n"
                "USW00093817  38.0400  -87.5300  118.0 EVANSVILLE         IN US\n"
            ).encode()
        if "sstoi.indices" in url:
            return _nino()
        if "USW00014848" in url:
            return _gz(["USW00014848,20181012,SNOW,25,,,"])
        return _gz(["USW00014827,20181012,TMIN,0,,,"])

    with pytest.raises(FetchError, match="required core USW00014848"):
        fetch_live(cache_dir=tmp_path, getter=getter)
