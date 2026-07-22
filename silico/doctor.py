"""Host environment and port doctor (read-only)."""

from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

from silico import __version__
from silico.deploy_idf import idf_py_available
from silico.mpy_pin import PLATE_DEFAULT_MPY_CROSS, pin_advice_lines, read_toml_mpy_cross
from silico.mpremote_util import mpremote_available
from silico.ports import IDENTITY_HINT, list_scored_ports
from silico.runtime import runtime_summary_lines, resolve_runtime
from silico.workspace import detect_workspace


@dataclass
class DoctorReport:
    ok: bool
    lines: list[str] = field(default_factory=list)


def run_doctor(*, root: Path | None = None) -> DoctorReport:
    lines: list[str] = []
    ok = True

    lines.append(f"silico {__version__}")
    py = sys.version.split()[0]
    lines.append(f"Python {py} ({sys.executable})")

    ws = detect_workspace(root)
    lines.append(f"Workspace mode: {ws.mode} ({ws.root})")
    for r in ws.reasons:
        lines.append(f"  - {r}")
    if ws.mode == "silico-package":
        lines.append(
            "INFO: this tree is the silico package. Product Day 1 work belongs in a GCU repo "
            "(do not scaffold a GCU into the silico checkout)."
        )
    elif ws.mode == "gcu":
        lines.append(
            "INFO: this tree looks like a GCU product root — scaffold/merge plate here (silico scaffold .)."
        )
    else:
        lines.append(
            "INFO: workspace unknown — if the operator started you inside a product checkout, "
            "cd there; if empty, scaffold into a new product directory (not named silico)."
        )
    if sys.version_info < (3, 11):
        lines.append("FAIL: need Python 3.11+")
        ok = False
    else:
        lines.append("OK: Python >= 3.11")

    if shutil.which("git"):
        lines.append("OK: git on PATH")
    else:
        lines.append("WARN: git not on PATH")

    cfg = resolve_runtime(root)
    lines.extend(runtime_summary_lines(cfg))
    if cfg.errors:
        ok = False

    # Tooling hints for C intent even if config has FAILs (language still "c").
    if cfg.language == "c":
        if idf_py_available():
            lines.append("OK: ESP-IDF tools available (idf.py or IDF_PATH)")
        else:
            lines.append(
                "WARN: ESP-IDF tools not found — language=c deploy needs idf.py / IDF_PATH"
            )
        if shutil.which("cmake"):
            lines.append("OK: cmake on PATH (C host gate)")
        else:
            lines.append("WARN: cmake not on PATH (needed for C host gate)")
    else:
        if mpremote_available():
            lines.append("OK: mpremote available (device ops)")
        else:
            lines.append(
                "WARN: mpremote not found - install for deploy/inspect (pip install mpremote)"
            )

        toml_pin = read_toml_mpy_cross(root)
        if toml_pin:
            lines.append(f"silico.toml mpy_cross={toml_pin}")
            if toml_pin == "1.22.2":
                lines.append(
                    f"WARN: mpy_cross still at ancient plate value 1.22.2; "
                    f"re-pin after inspect (plate default is now {PLATE_DEFAULT_MPY_CROSS})."
                )
            for line in pin_advice_lines(None, toml_pin):
                lines.append(line)
        else:
            lines.append(
                f"INFO: no silico.toml mpy_cross yet (scaffold plate default {PLATE_DEFAULT_MPY_CROSS}; "
                "re-pin to device MicroPython after inspect)."
            )

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
                "INFO: no preferred board (score>=50). Pass --port after operator confirms. "
                "Do not assume a demoted adapter is the product board."
            )

    # Point agents at growing host knowledge (board caps, audio, first-flash).
    lines.append(
        "Host knowledge: silico/knowledge/ (ESP32 audio, first-flash notes). "
        "When Day 1 friction is board/host-generic, add a note there (Make it better)."
    )

    return DoctorReport(ok=ok, lines=lines)
