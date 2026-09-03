# Copyright (c) 2026 Martial Systems LLC


class GateError(RuntimeError):
    """Stage hard gate failed."""


class ClaimBanError(GateError):
    """Report text hit a banned claim."""


class FetchError(GateError):
    """GHCND TMIN, October climate, or Niño 3.4 empty, or a refused substitute."""


class SplitError(GateError):
    """Temporal split leaked confirmation into train or the median."""


class FigureCapError(GateError):
    """This tree stops at two figures."""


class LeakError(GateError):
    """Same-window TMIN or a banned token appeared in the feature vector."""
