"""Detect whether cwd is a GCU product tree, a silico package checkout, or unknown."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ImportError:  # pragma: no cover — py3.11+
    tomllib = None  # type: ignore


@dataclass(frozen=True)
class WorkspaceKind:
    """mode: gcu | silico-package | unknown"""

    mode: str
    root: Path
    reasons: tuple[str, ...]


def _project_name(pyproject: Path) -> str | None:
    """Return [project].name (or tool.poetry.name) from pyproject.toml."""
    if tomllib is None:
        return None
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        return None
    name = data.get("project", {}).get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    poetry = data.get("tool", {}).get("poetry", {})
    pname = poetry.get("name") if isinstance(poetry, dict) else None
    if isinstance(pname, str) and pname.strip():
        return pname.strip()
    return None


def detect_workspace(root: Path | None = None) -> WorkspaceKind:
    """Classify the working tree for Day 1 agents (no product names)."""
    root = (root or Path.cwd()).resolve()
    reasons: list[str] = []

    plates = root / "silico" / "plates"
    pyproject = root / "pyproject.toml"
    if plates.is_dir() and pyproject.is_file():
        proj = _project_name(pyproject)
        if proj in ("tig-silico", "silico"):
            reasons.append(f"silico/plates/ present; pyproject [project].name={proj!r}")
            return WorkspaceKind("silico-package", root, tuple(reasons))
        if proj is None:
            # plates layout without parseable name — still treat as silico source tree
            reasons.append("silico/plates/ present with pyproject.toml")
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

    if (
        (root / "spec.md").is_file()
        or (root / "silico.toml").is_file()
        or (root / "firmware").is_dir()
    ):
        return WorkspaceKind("gcu", root, tuple(reasons))

    return WorkspaceKind(
        "unknown", root, tuple(reasons) if reasons else ("no product markers",)
    )
