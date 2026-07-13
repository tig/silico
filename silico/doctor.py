"""Host environment and port doctor (read-only)."""

from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass, field

from silico import __version__
from silico.mpremote_util import mpremote_available
from silico.ports import IDENTITY_HINT, list_scored_ports


@dataclass
class DoctorReport:
    ok: bool
    lines: list[str] = field(default_factory=list)


def run_doctor() -> DoctorReport:
    lines: list[str] = []
    ok = True

    lines.append(f"silico {__version__}")
    py = sys.version.split()[0]
    lines.append(f"Python {py} ({sys.executable})")
    if sys.version_info < (3, 11):
        lines.append("FAIL: need Python 3.11+")
        ok = False
    else:
        lines.append("OK: Python >= 3.11")

    if shutil.which("git"):
        lines.append("OK: git on PATH")
    else:
        lines.append("WARN: git not on PATH")

    if mpremote_available():
        lines.append("OK: mpremote available (device ops)")
    else:
        lines.append("WARN: mpremote not found - install for deploy/inspect (pip install mpremote)")

    ports = list_scored_ports()
    preferred = [p for p in ports if p.score >= 50]
    if not ports:
        lines.append("INFO: no serial ports seen (plug a data USB cable; agent should poll, not ask)")
    else:
        lines.append("Serial ports (higher score first):")
        for p in ports:
            vid = f"{p.vid:04x}" if p.vid is not None else "----"
            pid = f"{p.pid:04x}" if p.pid is not None else "----"
            lines.append(f"  {p.device}  vid={vid} pid={pid}  score={p.score} - {p.label}")
            if p.description:
                lines.append(f"    {p.description}")
        if preferred:
            lines.append(IDENTITY_HINT)
        else:
            lines.append(
                "INFO: no preferred board (score>=50). Do not assume CH340 is the product board."
            )

    return DoctorReport(ok=ok, lines=lines)
