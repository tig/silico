"""Pull device files to host (backup before overwrite)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from silico.mpremote_util import ls_device, mpremote_available, run_mpremote
from silico.ports import pick_best_port, port_is_listed
from silico.progress import ProgressCallback, ProgressLog, file_step, stage_header


@dataclass
class PullResult:
    ok: bool
    lines: list[str] = field(default_factory=list)


# Banner / REPL noise (case-insensitive start or substring).
_NOISE_PREFIXES = (
    "ls ",
    "ls:",
    ">>>",
    "...",
    "mpy:",
    "micropython ",
    "type \"help",
    "type 'help",
    "traceback",
    "file \"",
    "  file \"",
)


def _is_noise_line(line: str) -> bool:
    low = line.lower().strip()
    if not low:
        return True
    for p in _NOISE_PREFIXES:
        if low.startswith(p) or p in low and low.startswith("mpy"):
            return True
    if low.startswith("mpy:") or "soft reboot" in low:
        return True
    if "traceback (most recent" in low:
        return True
    # Bare prompt crumbs
    if low in {">>>", "...", "soft reboot"}:
        return True
    return False


def _parse_ls_names(ls_stdout: str) -> list[str]:
    """Parse mpremote ls output into remote basenames (skip dirs).

    Tolerates banners and size-prefixed rows. Keeps extensionless files
    (e.g. ``config``, ``README``) while dropping pure noise tokens.
    """
    names: list[str] = []
    for raw in (ls_stdout or "").splitlines():
        line = raw.strip()
        if not line or _is_noise_line(line):
            continue
        parts = line.split()
        if not parts:
            continue
        # Size-prefixed: "   182 boot.py" or bare "boot.py"
        if len(parts) >= 2 and parts[0].lstrip("-").isdigit():
            name = parts[-1]
        elif len(parts) == 1:
            name = parts[0]
        else:
            # Multi-token non-size lines are usually banners
            if any(w.lower() in {"reboot", "exception", "error"} for w in parts[:-1]):
                continue
            name = parts[-1]
        if name.startswith(":"):
            name = name[1:]
        if name.endswith("/"):
            continue
        if name in (".", ".."):
            continue
        if name.isdigit():
            continue
        # Reject tokens that are only punctuation
        if not any(c.isalnum() or c in "._-" for c in name):
            continue
        # Single all-lowercase English noise words without digits/ext
        if "." not in name and name.lower() in {
            "reboot",
            "reset",
            "soft",
            "hard",
            "ok",
            "fail",
            "error",
            "help",
            "type",
            "for",
            "more",
            "information",
        }:
            continue
        names.append(name)
    seen: set[str] = set()
    out: list[str] = []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def pull_device(
    dest: Path,
    *,
    port: str | None = None,
    only: list[str] | None = None,
    on_progress: ProgressCallback | None = None,
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
    log = ProgressLog(on_progress)
    log(stage_header("pull", f"{chosen.device} -> {dest}"))

    ls = ls_device(chosen.device)
    if ls.returncode != 0:
        log("FAIL: ls device")
        if ls.stderr:
            log(ls.stderr.strip())
        return PullResult(False, log.lines)
    names = _parse_ls_names(ls.stdout or "")
    if only:
        want = set(only)
        names = [n for n in names if n in want]
    if not names:
        log("INFO: no files to pull")
        return PullResult(True, log.lines)

    n = len(names)
    log(f"PROGRESS [pull] {n} file(s) to copy")
    ok = True
    for i, name in enumerate(names, start=1):
        local = dest / name
        log(file_step(stage="pull", index=i, total=n, name=name, verb="Reading"))
        r = run_mpremote(chosen.device, "cp", f":{name}", str(local))
        if r.returncode != 0:
            ok = False
            log(f"FAIL: :{name} -> {local}")
            if r.stderr:
                log(r.stderr.strip())
        else:
            log(f"OK: :{name} -> {local}")
    log(stage_header("done", "pull finished " + ("OK" if ok else "with errors")))
    return PullResult(ok, log.lines)
