"""Single place to choose MicroPython vs ESP-IDF backend from RuntimeConfig."""

from __future__ import annotations

from silico.runtime import RuntimeConfig

BACKEND_MPY = "mpy"
BACKEND_IDF = "idf"
BACKEND_INVALID = "invalid"


def backend_kind(cfg: RuntimeConfig) -> str:
    """Return ``mpy``, ``idf``, or ``invalid`` (config FAIL — do not deploy)."""
    if not cfg.ok:
        return BACKEND_INVALID
    if cfg.is_c:
        return BACKEND_IDF
    return BACKEND_MPY


def is_idf(cfg: RuntimeConfig) -> bool:
    return backend_kind(cfg) == BACKEND_IDF


def is_mpy(cfg: RuntimeConfig) -> bool:
    return backend_kind(cfg) == BACKEND_MPY
