"""Detect whether cwd is a GCU product tree, a silico package checkout, or unknown."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorkspaceKind:
    """mode: gcu | silico-package | unknown"""

    mode: str
    root: Path
    reasons: tuple[str, ...]


def detect_workspace(root: Path | None = None) -> WorkspaceKind:
    """Classify the working tree for Day 1 agents (no product names)."""
    root = (root or Path.cwd()).resolve()
    reasons: list[str] = []

    plates = root / "silico" / "plates"
    pyproject = root / "pyproject.toml"
    if plates.is_dir() and pyproject.is_file():
        try:
            text = pyproject.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        if "tig-silico" in text or 'name = "silico"' in text or "name='silico'" in text:
            reasons.append("silico/plates/ present with silico pyproject")
            return WorkspaceKind("silico-package", root, tuple(reasons))

    if (root / "spec.md").is_file():
        reasons.append("spec.md present")
    if (root / "silico.toml").is_file():
        reasons.append("silico.toml present")
    if (root / "firmware").is_dir():
        reasons.append("firmware/ present")
    if (root / "requirements-dev.txt").is_file():
        reasons.append("requirements-dev.txt present")
    agents = root / "AGENTS.md"
    if agents.is_file():
        try:
            a = agents.read_text(encoding="utf-8", errors="replace")
        except OSError:
            a = ""
        if "tig-silico" in a or "silico" in a.lower():
            reasons.append("AGENTS.md references silico")

    if reasons and "silico/plates/" not in " ".join(reasons):
        # Product-ish tree (spec-only GCU counts if spec.md alone)
        if (
            (root / "spec.md").is_file()
            or (root / "silico.toml").is_file()
            or (root / "firmware").is_dir()
        ):
            return WorkspaceKind("gcu", root, tuple(reasons))

    return WorkspaceKind("unknown", root, tuple(reasons) if reasons else ("no product markers",))
