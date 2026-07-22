"""ESP-IDF image deploy (build + flash) for language=c GCUs."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from silico.config_toml import read_product_identity
from silico.deploy_types import DeployPlan, DeployResult
from silico.ports import IDENTITY_HINT, pick_best_port, port_is_listed
from silico.runtime import RuntimeConfig, resolve_runtime
from silico.serial_identity import probe_serial_identity


def idf_py_available() -> bool:
    return shutil.which("idf.py") is not None or bool(os.environ.get("IDF_PATH"))


def _idf_py_invocation() -> list[str]:
    """Return argv prefix to run idf.py (PATH or $IDF_PATH/tools/idf.py)."""
    which = shutil.which("idf.py")
    if which:
        return [which]
    idf_path = os.environ.get("IDF_PATH")
    if idf_path:
        candidate = Path(idf_path) / "tools" / "idf.py"
        if candidate.is_file():
            return [sys.executable, str(candidate)]
    return ["idf.py"]


def plan_idf_deploy(
    *,
    port: str | None = None,
    root: Path | None = None,
    cfg: RuntimeConfig | None = None,
) -> DeployPlan | DeployResult:
    root = (root or Path.cwd()).resolve()
    cfg = cfg or resolve_runtime(root)

    if cfg.errors:
        return DeployResult(False, list(cfg.errors))

    if not port:
        return DeployResult(
            False,
            [
                "FAIL: deploy requires explicit --port after operator confirms device identity.",
                "Do not auto-pick a COM from score alone.",
            ],
        )

    chosen = pick_best_port(port)
    if chosen is None:
        return DeployResult(
            False,
            [
                "FAIL: no preferred board port. Use silico wait-device or --port.",
            ],
        )
    if not port_is_listed(chosen.device):
        return DeployResult(
            False,
            [
                f"FAIL: port {chosen.device} is not in the current serial inventory.",
                "Re-run wait-device; re-confirm identity.",
            ],
        )

    proj_rel = cfg.project or "firmware"
    project = (root / proj_rel).resolve()
    if not project.is_dir():
        return DeployResult(
            False,
            [
                f"FAIL: IDF project directory missing: {proj_rel}",
                "Create firmware/ (ESP-IDF app) or set [deploy].project in silico.toml.",
            ],
        )

    chip = cfg.chip or "esp32"
    idf = _idf_py_invocation()
    build_cmd = [*idf, "-C", str(project), "build"]
    flash_cmd = [
        *idf,
        "-C",
        str(project),
        "-p",
        chosen.device,
        "flash",
    ]

    lines = [
        f"Planned IDF image write to {chosen.device} ({chosen.label}):",
        "This will OVERWRITE the entire application image on the device.",
        IDENTITY_HINT,
        f"  language: {cfg.language}  toolchain: {cfg.toolchain}  chip: {chip}",
    ]
    if cfg.esp_idf:
        lines.append(f"  esp_idf pin (docs): {cfg.esp_idf}")
    lines.append(f"  project: {proj_rel}")
    lines.append(f"  build: {' '.join(build_cmd)}")
    lines.append(f"  flash: {' '.join(flash_cmd)}")
    if not idf_py_available():
        lines.append(
            "WARN: idf.py not on PATH and IDF_PATH unset — write will fail until ESP-IDF is installed."
        )
    lines.append("Refusing to write without explicit confirmation (--yes).")
    lines.append(
        "Operator must have confirmed BOTH: (1) this port is the product board, "
        "(2) the application image may be overwritten."
    )
    lines.append(f"Inspect first: silico inspect --port {chosen.device}")
    return DeployPlan(
        port=chosen.device,
        lines=lines,
        files=[],
        kind="idf",
        project=project,
        chip=chip,
        build_cmd=build_cmd,
        flash_cmd=flash_cmd,
    )


def _run(cmd: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )


def deploy_idf(
    *,
    port: str | None = None,
    yes: bool = False,
    verify: bool = False,
    expect_name: str | None = None,
    expect_version: str | None = None,
    root: Path | None = None,
    run_fn=_run,
) -> DeployResult:
    root = (root or Path.cwd()).resolve()
    cfg = resolve_runtime(root)
    planned = plan_idf_deploy(port=port, root=root, cfg=cfg)
    if isinstance(planned, DeployResult):
        return planned

    lines = list(planned.lines)
    if not yes:
        lines.append(
            "ABORTED: pass --yes only after the operator explicitly confirmed the write."
        )
        return DeployResult(False, lines)

    if not idf_py_available():
        lines.append(
            "FAIL: ESP-IDF tools not found (idf.py / IDF_PATH). "
            "Install per Espressif getting started; silico doctor reports this."
        )
        return DeployResult(False, lines)

    if not port_is_listed(planned.port):
        lines.append(
            f"FAIL: port {planned.port} disappeared before write. Re-discover and re-confirm."
        )
        return DeployResult(False, lines)

    if not planned.build_cmd or not planned.flash_cmd:
        lines.append("FAIL: internal error — IDF plan missing build/flash commands.")
        return DeployResult(False, lines)

    lines.append("Confirmed (--yes). Building...")
    build = run_fn(planned.build_cmd, cwd=root)
    if build.returncode != 0:
        lines.append("FAIL: idf.py build")
        if build.stderr:
            lines.append(build.stderr.strip()[-2000:])
        elif build.stdout:
            lines.append(build.stdout.strip()[-2000:])
        return DeployResult(False, lines)
    lines.append("OK: build")

    lines.append("Flashing application image...")
    flash = run_fn(planned.flash_cmd, cwd=root)
    if flash.returncode != 0:
        lines.append("FAIL: idf.py flash")
        if flash.stderr:
            lines.append(flash.stderr.strip()[-2000:])
        elif flash.stdout:
            lines.append(flash.stdout.strip()[-2000:])
        return DeployResult(False, lines)
    lines.append("OK: flash")

    if verify:
        name, ver = read_product_identity(root)
        en = expect_name if expect_name is not None else name
        ev = expect_version if expect_version is not None else ver
        lines.append("Verify: serial identity after flash...")
        if not port_is_listed(planned.port):
            lines.append(
                f"WARN: port {planned.port} not listed after flash; still trying identity probe."
            )
        probe = probe_serial_identity(
            planned.port,
            baud=cfg.baud,
            expect_name=en,
            expect_version=ev,
        )
        lines.extend(probe.lines)
        if not probe.ok:
            return DeployResult(False, lines)
        lines.append("OK: identity verify")

    return DeployResult(True, lines)
