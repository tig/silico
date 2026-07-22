"""Shared deploy plan/result types (mpy file-copy and IDF image flash)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DeployPlan:
    """Planned write. kind distinguishes file-copy (mpy) vs full image (idf)."""

    port: str
    lines: list[str] = field(default_factory=list)
    files: list[tuple[Path, str]] = field(default_factory=list)
    prune_remotes: list[str] = field(default_factory=list)
    kind: str = "mpy"  # "mpy" | "idf"
    project: Path | None = None
    chip: str | None = None
    build_cmd: list[str] | None = None
    flash_cmd: list[str] | None = None


@dataclass
class DeployResult:
    ok: bool
    lines: list[str] = field(default_factory=list)
