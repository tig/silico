"""ESP-IDF image deploy (build + flash) for language=c GCUs."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from silico.config_toml import read_product_identity
from silico.deploy_types import DeployPlan, DeployResult
from silico.esptool_util import esptool_available, esptool_cmd_prefix, run_esptool_streaming
from silico.partition_data import (
    esptool_write_flash_args,
    plan_data_lines,
    resolve_data_assets,
)
from silico.ports import IDENTITY_HINT, pick_best_port, port_is_listed
from silico.progress import ProgressCallback, ProgressLog, stage_header
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
        stage_header("plan", f"IDF image write to {chosen.device} ({chosen.label})"),
        "This will OVERWRITE the entire application image on the device.",
        IDENTITY_HINT,
        f"  language: {cfg.language}  toolchain: {cfg.toolchain}  chip: {chip}",
    ]
    if cfg.esp_idf:
        lines.append(f"  esp_idf pin (docs): {cfg.esp_idf}")
    lines.append(f"  project: {proj_rel}")
    lines.append(f"  build: {' '.join(build_cmd)}")
    lines.append(f"  flash: {' '.join(flash_cmd)}")

    data_assets, data_errs = resolve_data_assets(root, project=proj_rel)
    if data_errs:
        return DeployResult(False, lines + data_errs)
    data_tuples = [
        (a.name, a.host_path, a.offset, a.size) for a in data_assets
    ]
    lines.extend(plan_data_lines(data_assets, port=chosen.device))
    if data_assets and not esptool_available():
        lines.append(
            "WARN: esptool not found — [[deploy.data]] flash needs esptool after idf image write."
        )

    if not idf_py_available():
        lines.append(
            "WARN: idf.py not on PATH and IDF_PATH unset — write will fail until ESP-IDF is installed."
        )
    lines.append("Refusing to write without explicit confirmation (--yes).")
    lines.append(
        "Operator must have confirmed BOTH: (1) this port is the product board, "
        "(2) the application image may be overwritten"
        + (" and data partitions" if data_assets else "")
        + "."
    )
    lines.append(f"Inspect first: silico inspect --port {chosen.device}")
    lines.append(
        "Progress during --yes: PROGRESS [idf-build] / [idf-flash] stream from idf.py."
    )
    if data_assets:
        lines.append(
            "Progress for data: PROGRESS [esptool] write_flash per [[deploy.data]] asset."
        )
    return DeployPlan(
        port=chosen.device,
        lines=lines,
        files=[],
        kind="idf",
        project=project,
        chip=chip,
        build_cmd=build_cmd,
        flash_cmd=flash_cmd,
        data_assets=data_tuples,
    )


def _run(cmd: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    """Capture-only runner (tests inject this)."""
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )


def _run_streaming(
    cmd: list[str],
    *,
    cwd: Path,
    log: ProgressLog,
    stage: str,
    timeout: float | None = 3600.0,
) -> int:
    """Stream idf.py stdout/stderr into log (live operator progress)."""
    log(stage_header(stage, " ".join(cmd)))
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert proc.stdout is not None
    prefix = f"PROGRESS [{stage}] "
    buf = ""
    deadline = time.monotonic() + timeout if timeout else None
    try:
        while True:
            if deadline is not None and time.monotonic() > deadline:
                proc.kill()
                log(f"FAIL: {stage} timed out")
                proc.wait(timeout=5)
                return 124
            ch = proc.stdout.read(1)
            if ch:
                if ch in ("\n", "\r"):
                    line = buf.strip()
                    buf = ""
                    if line:
                        log(f"{prefix}{line}")
                else:
                    buf += ch
                continue
            if proc.poll() is not None:
                break
            time.sleep(0.02)
        if buf.strip():
            log(f"{prefix}{buf.strip()}")
        return int(proc.wait(timeout=5) or 0)
    except Exception:
        proc.kill()
        raise


def deploy_idf(
    *,
    port: str | None = None,
    yes: bool = False,
    verify: bool = False,
    expect_name: str | None = None,
    expect_version: str | None = None,
    root: Path | None = None,
    run_fn=_run,
    on_progress: ProgressCallback | None = None,
) -> DeployResult:
    root = (root or Path.cwd()).resolve()
    cfg = resolve_runtime(root)
    log = ProgressLog(on_progress)
    planned = plan_idf_deploy(port=port, root=root, cfg=cfg)
    if isinstance(planned, DeployResult):
        log.extend(planned.lines)
        return DeployResult(planned.ok, log.lines)

    log.extend(planned.lines)
    if not yes:
        log("ABORTED: pass --yes only after the operator explicitly confirmed the write.")
        return DeployResult(False, log.lines)

    if not idf_py_available():
        log(
            "FAIL: ESP-IDF tools not found (idf.py / IDF_PATH). "
            "Install per Espressif getting started; silico doctor reports this."
        )
        return DeployResult(False, log.lines)

    if not port_is_listed(planned.port):
        log(
            f"FAIL: port {planned.port} disappeared before write. Re-discover and re-confirm."
        )
        return DeployResult(False, log.lines)

    if not planned.build_cmd or not planned.flash_cmd:
        log("FAIL: internal error — IDF plan missing build/flash commands.")
        return DeployResult(False, log.lines)

    # Default production path streams; tests inject run_fn (capture).
    use_stream = run_fn is _run

    log(stage_header("idf-build", "Confirmed (--yes). Building…"))
    if use_stream:
        code = _run_streaming(
            planned.build_cmd, cwd=root, log=log, stage="idf-build"
        )
        if code != 0:
            log(f"FAIL: idf.py build (exit {code})")
            return DeployResult(False, log.lines)
    else:
        build = run_fn(planned.build_cmd, cwd=root)
        if build.returncode != 0:
            log("FAIL: idf.py build")
            if build.stderr:
                log(build.stderr.strip()[-2000:])
            elif build.stdout:
                log(build.stdout.strip()[-2000:])
            return DeployResult(False, log.lines)
    log("OK: build")

    log(stage_header("idf-flash", "Flashing application image…"))
    if use_stream:
        code = _run_streaming(
            planned.flash_cmd, cwd=root, log=log, stage="idf-flash"
        )
        if code != 0:
            log(f"FAIL: idf.py flash (exit {code})")
            return DeployResult(False, log.lines)
    else:
        flash = run_fn(planned.flash_cmd, cwd=root)
        if flash.returncode != 0:
            log("FAIL: idf.py flash")
            if flash.stderr:
                log(flash.stderr.strip()[-2000:])
            elif flash.stdout:
                log(flash.stdout.strip()[-2000:])
            return DeployResult(False, log.lines)
    log("OK: flash")

    # Data partitions (same --yes; already announced in plan).
    if planned.data_assets:
        chip = planned.chip or "esp32"
        if not esptool_available():
            log(
                "FAIL: esptool required for [[deploy.data]] assets "
                "(pip install esptool)."
            )
            return DeployResult(False, log.lines)
        log(
            stage_header(
                "data-flash",
                f"{len(planned.data_assets)} data partition asset(s)…",
            )
        )
        for name, host_path, offset, size in planned.data_assets:
            log(
                f"Writing data {name!r}: {host_path.name} ({size} bytes) @ 0x{offset:x}"
            )
            args = esptool_write_flash_args(
                port=planned.port,
                chip=chip,
                offset=offset,
                file_path=host_path,
            )
            if use_stream:
                code = run_esptool_streaming(args, log=log)
                if code != 0:
                    log(f"FAIL: esptool write_flash {name!r} (exit {code})")
                    return DeployResult(False, log.lines)
            else:
                cmd = [*esptool_cmd_prefix(), *args]
                flash_d = run_fn(cmd, cwd=root)
                if flash_d.returncode != 0:
                    log(f"FAIL: esptool write_flash {name!r}")
                    if flash_d.stderr:
                        log(flash_d.stderr.strip()[-1000:])
                    return DeployResult(False, log.lines)
            log(f"OK: data {name!r}")

    if verify:
        name, ver = read_product_identity(root)
        en = expect_name if expect_name is not None else name
        ev = expect_version if expect_version is not None else ver
        log(stage_header("verify", "serial identity after flash"))
        if not port_is_listed(planned.port):
            log(
                f"WARN: port {planned.port} not listed after flash; still trying identity probe."
            )
        probe = probe_serial_identity(
            planned.port,
            baud=cfg.baud,
            expect_name=en,
            expect_version=ev,
        )
        log.extend(probe.lines)
        if not probe.ok:
            return DeployResult(False, log.lines)
        log("OK: identity verify")

    log(stage_header("done", "IDF deploy finished OK"))
    return DeployResult(True, log.lines)
