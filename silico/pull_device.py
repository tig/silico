"""Pull device files to host (backup before overwrite)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from silico.mpremote_util import ls_device, mpremote_available, run_mpremote
from silico.ports import pick_best_port, port_is_listed


@dataclass
class PullResult:
    ok: bool
    lines: list[str] = field(default_factory=list)


def _parse_ls_names(ls_stdout: str) -> list[str]:
    """Parse mpremote ls output into remote basenames (skip dirs)."""
    names: list[str] = []
    for line in (ls_stdout or "").splitlines():
        line = line.strip()
        if not line or line.startswith("ls "):
            continue
        # formats: "   1234 name.py" or "name.py"
        parts = line.split()
        if not parts:
            continue
        name = parts[-1]
        if name.endswith("/"):
            continue
        if name in (".", ".."):
            continue
        names.append(name)
    return names


def pull_device(
    dest: Path,
    *,
    port: str | None = None,
    only: list[str] | None = None,
) -> PullResult:
    if not mpremote_available():
        return PullResult(False, ["FAIL: mpremote not available"])
    chosen = pick_best_port(port)
    if chosen is None:
        return PullResult(False, ["FAIL: no preferred port; pass --port"])
    if port and not port_is_listed(chosen.device):
        return PullResult(False, [f"FAIL: port {chosen.device} not in inventory"])

    dest = dest.resolve()
    dest.mkdir(parents=True, exist_ok=True)
    lines = [f"Pull from {chosen.device} -> {dest}"]

    ls = ls_device(chosen.device)
    if ls.returncode != 0:
        return PullResult(False, lines + ["FAIL: ls device", (ls.stderr or "").strip()])
    names = _parse_ls_names(ls.stdout or "")
    if only:
        want = set(only)
        names = [n for n in names if n in want]
    if not names:
        lines.append("INFO: no files to pull")
        return PullResult(True, lines)

    ok = True
    for name in names:
        local = dest / name
        r = run_mpremote(chosen.device, "cp", f":{name}", str(local))
        if r.returncode != 0:
            ok = False
            lines.append(f"FAIL: :{name} -> {local}")
            if r.stderr:
                lines.append(r.stderr.strip())
        else:
            lines.append(f"OK: :{name} -> {local}")
    return PullResult(ok, lines)
