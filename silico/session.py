"""First-ship session / provenance record (tig/silico#84).

Records start commit and mode so agents cannot silently lose the distinction
between authored-this-run and past-HEAD salvage. State is gitignored under
``.silico/session.toml``.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

try:
    import tomllib
except ImportError:  # pragma: no cover
    tomllib = None  # type: ignore


SESSION_REL = Path(".silico") / "session.toml"


@dataclass
class SessionReport:
    ok: bool
    lines: list[str] = field(default_factory=list)
    path: Path | None = None


def session_path(root: Path | None = None) -> Path:
    return (root or Path.cwd()).resolve() / SESSION_REL


def _git(root: Path, *args: str) -> str:
    try:
        r = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"(git failed: {e})"
    if r.returncode != 0:
        return (r.stderr or r.stdout or "git error").strip() or "(git error)"
    return (r.stdout or "").strip()


def _toml_str(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def start_session(
    *,
    root: Path | None = None,
    mode: str = "evaluation",
    agent: str = "",
    workflow: str = "main",
) -> SessionReport:
    """Record first-ship start provenance at cwd (or *root*)."""
    root = (root or Path.cwd()).resolve()
    mode = (mode or "evaluation").strip().lower()
    if mode not in ("evaluation", "product-update"):
        return SessionReport(
            False,
            [f"FAIL: mode must be evaluation or product-update, got {mode!r}"],
        )
    workflow = (workflow or "main").strip().lower()
    if workflow not in ("main", "branch"):
        return SessionReport(
            False,
            [f"FAIL: workflow must be main or branch, got {workflow!r}"],
        )

    head = _git(root, "rev-parse", "HEAD")
    branch = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
    remote = _git(root, "remote", "get-url", "origin")
    if remote.startswith("(git"):
        remote = ""
    host = sys.platform
    agent = (agent or "").strip() or "unknown"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines_out = [
        "# silico first-ship session (gitignored). Do not commit.",
        f"started_at = {_toml_str(now)}",
        f"root = {_toml_str(str(root))}",
        f"start_commit = {_toml_str(head)}",
        f"branch = {_toml_str(branch)}",
        f"remote = {_toml_str(remote)}",
        f"mode = {_toml_str(mode)}",
        f"workflow = {_toml_str(workflow)}",
        f"host = {_toml_str(host)}",
        f"agent = {_toml_str(agent)}",
        "",
        "# Reset recipe (destructive — operator gate required before running):",
        f"#   git fetch origin && git reset --hard {head}",
        f"#   git clean -fd  # optional; drops untracked",
        "",
    ]
    path = session_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines_out) + "\n", encoding="utf-8")

    report_lines = [
        f"OK: session written {path}",
        f"  start_commit={head}",
        f"  branch={branch}",
        f"  mode={mode}  workflow={workflow}",
        f"  host={host}  agent={agent}",
        "Reset recipe (operator go required before hard reset):",
        f"  git fetch origin && git reset --hard {head}",
        "Prior-attempt discovery: do not cherry-pick/replay older product commits "
        "unless operator chooses reuse-prior-attempt (see AGENTS Product truth is HEAD).",
    ]
    return SessionReport(True, report_lines, path=path)


def show_session(*, root: Path | None = None) -> SessionReport:
    root = (root or Path.cwd()).resolve()
    path = session_path(root)
    if not path.is_file():
        return SessionReport(
            False,
            [
                "FAIL: no session file.",
                "What to do next: silico session start --mode evaluation",
            ],
        )
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = [f"Session file: {path}", "---"]
    lines.extend(text.splitlines())
    data: dict = {}
    if tomllib is not None:
        try:
            # strip comment-only lines for tomllib by reading non-comment body
            body = "\n".join(
                ln for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")
            )
            data = tomllib.loads(body) if body.strip() else {}
        except Exception:  # noqa: BLE001
            data = {}
    start = data.get("start_commit", "")
    if start:
        lines.append("---")
        lines.append(f"Reset recipe: git fetch origin && git reset --hard {start}")
    return SessionReport(True, lines, path=path)
