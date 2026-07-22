"""Operator-visible progress lines for deploy / flash / pull.

Agents and the CLI print these as they happen (flush), so a multi-minute
esptool write or multi-file mpremote deploy is not a silent black box.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

# Optional live sink: print each line as soon as it is produced.
ProgressCallback = Callable[[str], None]


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


def emit(
    lines: list[str],
    message: str,
    *,
    on_progress: ProgressCallback | None = None,
) -> None:
    """Record a line and optionally stream it live to the operator."""
    lines.append(message)
    if on_progress is not None:
        on_progress(message)


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
