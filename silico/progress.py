"""Operator-visible progress for deploy / flash / pull.

One sink owns the durable transcript *and* optional live streaming so call
sites do not dual-bookkeep ``lines`` + ``on_progress``.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path

ProgressCallback = Callable[[str], None]


class ProgressLog:
    """Transcript + optional live callback.

    ``log("msg")`` appends to ``log.lines`` and, if set, invokes the callback.
    Mid-stream tool output (esptool, UF2 copy) should use the same log so
    ``result.lines`` is a full record.
    """

    def __init__(self, on_progress: ProgressCallback | None = None) -> None:
        self.lines: list[str] = []
        self._cb = on_progress

    def __call__(self, message: str) -> None:
        self.lines.append(message)
        if self._cb is not None:
            self._cb(message)

    def extend(self, messages: Iterable[str]) -> None:
        for m in messages:
            self(m)


def format_bytes(n: int) -> str:
    """Human size for progress lines (binary units)."""
    if n < 0:
        return "?"
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KiB"
    return f"{n / (1024 * 1024):.2f} MiB"


def file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return -1


def stage_header(stage: str, detail: str = "") -> str:
    if detail:
        return f"PROGRESS [{stage}] {detail}"
    return f"PROGRESS [{stage}]"


def file_step(
    *,
    stage: str,
    index: int,
    total: int,
    name: str,
    size: int | None = None,
    verb: str = "Writing",
) -> str:
    """e.g. PROGRESS [write] 2/7 main.py (12.4 KiB) — Writing…"""
    size_s = f" ({format_bytes(size)})" if size is not None and size >= 0 else ""
    return f"PROGRESS [{stage}] {index}/{total} {name}{size_s} — {verb}…"


def cp_timeout_for_size(size: int) -> float:
    """Wall-clock budget for one mpremote cp (no byte bar from mpremote).

    Floor 30s; add ~1s per 50 KiB; cap 600s for large audio assets.
    """
    if size <= 0:
        return 30.0
    return max(30.0, min(600.0, 30.0 + size / 50_000.0))
