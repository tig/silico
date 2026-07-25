"""Host environment and port doctor (read-only)."""

from __future__ import annotations

import importlib
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


def host_python_health_lines(*, import_module=None) -> tuple[bool, list[str]]:
    """Check stdlib C-extension linkage that ESP-IDF tooling depends on (#87).

    Homebrew pythons can rot (pyexpat linked against a removed libexpat),
    which breaks idf_tools.py / install.sh in confusing ways. Surface it
    here with an actionable fix instead of letting ESP-IDF installs fail.
    """
    imp = import_module or importlib.import_module
    try:
        imp("pyexpat")
    except Exception as e:  # ImportError or loader-level OSError
        return False, [
            f"WARN: stdlib pyexpat is broken ({e}) — typical Homebrew python "
            "linkage rot; ESP-IDF installers need it. Fix: use a uv-managed "
            "interpreter (`uv venv --python 3.11`) or reinstall python.",
        ]
    return True, ["OK: pyexpat imports (stdlib XML linkage healthy)"]


_CMAKE_PROBE_DIRS = (Path("/opt/homebrew/bin"), Path("/usr/local/bin"))


def cmake_hint_lines(*, which=shutil.which, probe_dirs=None) -> list[str]:
    """cmake presence for the C host gate, with an off-PATH rescue hint (#87)."""
    if which("cmake"):
        return ["OK: cmake on PATH (C host gate)"]
    dirs = _CMAKE_PROBE_DIRS if probe_dirs is None else probe_dirs
    for d in dirs:
        cand = Path(d) / "cmake"
        if cand.is_file():
            return [
                f"WARN: cmake not on PATH but found at {cand} — add {d} to PATH "
                '(e.g. `eval "$(/opt/homebrew/bin/brew shellenv)"`).'
            ]
    return ["WARN: cmake not on PATH (needed for C host gate) — install via brew/apt or EIM"]


def esp_idf_summary_lines(tc, deploy_ready: bool) -> list[str]:
    """One honest ESP-IDF availability line for language=c (#87, PR #88 CR).

    ``deploy_ready`` must mirror what `silico deploy` actually accepts
    (idf.py on PATH or IDF_PATH). A catalog-only install (idf-env.json /
    EIM) is real but NOT deploy-ready until its export script is sourced —
    report needs-activation, never a false OK.
    """
    if deploy_ready:
        return [f"OK: ESP-IDF tools available ({tc.idf_py or 'idf.py on PATH / IDF_PATH'})"]
    if tc.idf_py:
        hint = ""
        if tc.selected and tc.selected.activation_script:
            hint = f' — activate: . "{tc.selected.activation_script}"'
        return [
            f"WARN: ESP-IDF installed but not activated ({tc.idf_py} via catalog); "
            "deploy needs idf.py on PATH or IDF_PATH" + hint
        ]
    return [
        "WARN: ESP-IDF tools not found — language=c deploy needs idf.py "
        "(PATH, IDF_PATH, EIM, or ~/.espressif/idf-env.json)"
    ]


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
            "INFO: this tree is the silico package. Product first-ship work belongs in a GCU repo "
            "(do not scaffold a GCU into the silico checkout)."
        )
    elif ws.mode == "gcu":
        lines.append(
            "INFO: this tree looks like a GCU product root — scaffold/merge plate here (silico scaffold .)."
        )
        bedside_toml = (ws.root / "bedside.toml") if ws.root else (Path.cwd() / "bedside.toml")
        if not bedside_toml.is_file():
            lines.append(
                "WARN: bedside.toml missing in GCU root — manners pin absent; "
                "scaffold plate (ships bedside.toml) or copy from silico plates; "
                "do not invent a parallel operator path."
            )
        else:
            try:
                import tomllib

                data = tomllib.loads(bedside_toml.read_text(encoding="utf-8"))
                cpath = data.get("contract_path", "")
                resolved = (ws.root / cpath).resolve() if cpath and ws.root else None
                if resolved is not None and not (
                    resolved.is_dir() and (resolved / "README.md").is_file()
                ):
                    lines.append(
                        f"WARN: bedside contract not found at {cpath} "
                        f"(resolved {resolved}) — clone silico as sibling or fix paths; "
                        "then `bedside doctor`. Do not skip ask/step."
                    )
                else:
                    lines.append(
                        f"OK: bedside.toml present (pin={data.get('pin', '?')}; "
                        "run `bedside doctor` before gates)."
                    )
            except Exception as e:
                lines.append(f"WARN: bedside.toml unreadable ({e})")
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
    _, py_health = host_python_health_lines()
    lines.extend(py_health)

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
        # One discovery pass drives both the summary line and the section
        # below, so they can't contradict each other (#87).
        from silico.c_toolchain import discover_c_toolchain, doctor_c_toolchain_lines

        tc = discover_c_toolchain()
        lines.extend(esp_idf_summary_lines(tc, deploy_ready=idf_py_available()))
        lines.extend(cmake_hint_lines())
        # EIM / idf_tools.py catalogs (#79, #87) — resolved paths, not hand-parsed JSON.
        lines.append("--- C toolchain (EIM / IDF) ---")
        lines.extend(doctor_c_toolchain_lines())
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
        "When first ship friction is board/host-generic, add a note there (Make it better)."
    )

    return DoctorReport(ok=ok, lines=lines)
