from __future__ import annotations

import os


def _float_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


API_VERSION = os.getenv("SKILLGRAPH_API_VERSION", "v1")

REQUIRED_MASTERY_THRESHOLD = _float_env("SKILLGRAPH_REQUIRED_THRESHOLD", 0.65)
PREFERRED_MASTERY_THRESHOLD = _float_env("SKILLGRAPH_PREFERRED_THRESHOLD", 0.5)

MISSING_GAP_DELTA = _float_env("SKILLGRAPH_MISSING_DELTA", 0.35)
WEAK_GAP_DELTA = _float_env("SKILLGRAPH_WEAK_DELTA", 0.15)
