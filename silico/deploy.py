"""Deploy application files with explicit confirmation and optional version verify."""

from __future__ import annotations

import re
import time
from pathlib import Path

from silico.backend import BACKEND_IDF, BACKEND_INVALID, backend_kind
from silico.config_toml import read_deploy_core
from silico.deploy_idf import deploy_idf, plan_idf_deploy
from silico.deploy_types import DeployPlan, DeployResult
from silico.identity import match_expected, parse_identity_blob
from silico.mpremote_util import cp_to_device, exec_on_device, ls_device, mpremote_available, run_mpremote
from silico.ports import IDENTITY_HINT, pick_best_port, port_is_listed
from silico.progress import (
    ProgressCallback,
    ProgressLog,
    cp_timeout_for_size,
    file_size,
    file_step,
    format_bytes,
    stage_header,
)
from silico.pull_device import _parse_ls_names
from silico.runtime import resolve_runtime

# Re-export for callers that import from silico.deploy
__all__ = ["DeployPlan", "DeployResult", "deploy", "plan_deploy", "resolve_deploy_files"]


# Modules that start an infinite loop when imported on-device (plate main.py).
_BOOT_ENTRY_MODULES = frozenset({"main"})


def _safe_module_name(name: str) -> str | None:
    n = name.strip()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", n):
        return None
    return n


def device_verify_import_snippet(mod: str) -> tuple[str, str]:
    """Build on-device code for --verify-import.

    Returns (code, mode) where mode is 'import' or 'compile'.
    Boot entry modules (e.g. main) are compile-checked only so the infinite
    device loop cannot hang mpremote (CR fix).
    """
    if mod in _BOOT_ENTRY_MODULES:
        code = (
            f"src=open('{mod}.py').read()\n"
            f"compile(src, '{mod}.py', 'exec')\n"
            f"print('compile_ok', '{mod}')\n"
        )
        return code, "compile"
    code = f"import {mod}\nprint('import_ok', '{mod}')\n"
    return code, "import"


def resolve_deploy_files(
    files: list[Path] | None,
    *,
    root: Path | None = None,
) -> list[Path] | DeployResult:
    """Use CLI files, or silico.toml [deploy].core when files empty."""
    if files:
        return list(files)
    core = read_deploy_core(root)
    if not core:
        return DeployResult(
            False,
            [
                "FAIL: no files given and no [deploy].core in silico.toml.",
                "Pass files on the CLI, or add:",
                "  [deploy]",
                '  core = ["firmware/version.py", "firmware/main.py"]',
            ],
        )
    root = root or Path.cwd()
    out: list[Path] = []
    for rel in core:
        p = (root / rel).resolve()
        if not p.is_file():
            return DeployResult(False, [f"FAIL: manifest file missing: {rel}"])
        out.append(p)
    return out


def plan_deploy(
    files: list[Path] | None,
    *,
    port: str | None = None,
    remote_names: list[str] | None = None,
    prune: bool = False,
    root: Path | None = None,
) -> DeployPlan | DeployResult:
    root = root or Path.cwd()
    cfg = resolve_runtime(root)
    kind = backend_kind(cfg)
    if kind == BACKEND_INVALID:
        return DeployResult(False, list(cfg.errors) or ["FAIL: invalid runtime config"])
    if kind == BACKEND_IDF:
        if files:
            return DeployResult(
                False,
                [
                    "FAIL: language=c / idf-flash deploy does not take file args.",
                    "Build and flash the IDF project ([deploy].project); omit file paths.",
                ],
            )
        if prune:
            return DeployResult(
                False,
                [
                    "FAIL: --prune is MicroPython-only (file copy). "
                    "C deploy overwrites the application image."
                ],
            )
        return plan_idf_deploy(port=port, root=root, cfg=cfg)

    if not mpremote_available():
        return DeployResult(False, ["FAIL: mpremote not available (pip install mpremote)"])

    if not port:
        return DeployResult(
            False,
            [
                "FAIL: deploy requires explicit --port after operator confirms device identity.",
                "Do not auto-pick a COM from score alone. Flow: wait-device -> doctor/inspect -> confirm -> deploy --port COMx",
            ],
        )

    chosen = pick_best_port(port)
    if chosen is None:
        return DeployResult(
            False,
            [
                "FAIL: no preferred board port. Use silico wait-device or --port.",
                "Refusing blind auto-connect on multi-device / CH340-only hosts.",
            ],
        )

    if not port_is_listed(chosen.device):
        return DeployResult(
            False,
            [
                f"FAIL: port {chosen.device} is not in the current serial inventory.",
                "Device may be unplugged or the COM number changed. Re-run wait-device; re-confirm identity.",
            ],
        )

    resolved = resolve_deploy_files(files, root=root)
    if isinstance(resolved, DeployResult):
        return resolved
    file_list = resolved

    pairs: list[tuple[Path, str]] = []
    total_bytes = 0
    lines = [
        stage_header("plan", f"deploy to {chosen.device} ({chosen.label})"),
        "This will OVERWRITE files on the device and may change boot behavior.",
        IDENTITY_HINT,
    ]
    if not files:
        lines.append("Using [deploy].core from silico.toml")
    n = len(file_list)
    for i, f in enumerate(file_list, start=1):
        path = Path(f)
        if not path.is_file():
            return DeployResult(False, [f"FAIL: not a file: {path}"])
        remote = remote_names[i - 1] if remote_names and i - 1 < len(remote_names) else path.name
        sz = file_size(path)
        if sz >= 0:
            total_bytes += sz
        pairs.append((path, remote))
        lines.append(
            f"  [{i}/{n}] {path}  ->  :{remote}  ({format_bytes(sz) if sz >= 0 else '?'})"
        )
    lines.append(f"Total payload: {format_bytes(total_bytes)} across {n} file(s)")
    lines.append(
        "Progress during --yes: PROGRESS [write] i/n name (size) for each file; "
        "then prune / reset / verify stages."
    )

    prune_remotes: list[str] = []
    if prune:
        ls = ls_device(chosen.device)
        if ls.returncode == 0:
            on_dev = set(_parse_ls_names(ls.stdout or ""))
            want = {remote for _, remote in pairs}
            prune_remotes = sorted(n for n in on_dev if n.endswith(".py") and n not in want)
            if prune_remotes:
                lines.append("Will REMOVE on device (--prune), .py not in manifest:")
                for name in prune_remotes:
                    lines.append(f"  delete :{name}")
            else:
                lines.append("Prune: no orphan .py files on device")
        else:
            lines.append("WARN: could not ls device for prune plan")

    lines.append("Refusing to write without explicit confirmation (--yes).")
    lines.append(
        "Operator must have confirmed BOTH: (1) this port is the product board, "
        "(2) these files may be written"
        + (" and orphans removed" if prune_remotes else "")
        + "."
    )
    lines.append("Inspect first: silico inspect --port " + chosen.device)
    return DeployPlan(
        port=chosen.device,
        files=pairs,
        lines=lines,
        prune_remotes=prune_remotes,
        kind="mpy",
    )


def _write_files(log: ProgressLog, planned: DeployPlan) -> bool:
    n = len(planned.files)
    total_b = sum(max(file_size(p), 0) for p, _ in planned.files)
    log(
        stage_header(
            "write",
            f"Confirmed (--yes). Copying {n} file(s), {format_bytes(total_b)} via mpremote…",
        )
    )
    for i, (local, remote) in enumerate(planned.files, start=1):
        sz = file_size(local)
        log(file_step(stage="write", index=i, total=n, name=remote, size=sz, verb="Writing"))
        t0 = time.monotonic()
        r = cp_to_device(planned.port, local, remote, timeout=cp_timeout_for_size(sz))
        elapsed = time.monotonic() - t0
        if r.returncode != 0:
            log(f"FAIL: cp {local} -> :{remote}")
            if r.stderr:
                log(r.stderr.strip())
            return False
        log(
            f"OK: wrote :{remote} ({format_bytes(sz) if sz >= 0 else '?'}) in {elapsed:.1f}s"
        )
    return True


def _prune_files(log: ProgressLog, planned: DeployPlan) -> None:
    if not planned.prune_remotes:
        return
    log(stage_header("prune", f"{len(planned.prune_remotes)} orphan .py"))
    for j, remote in enumerate(planned.prune_remotes, start=1):
        log(
            file_step(
                stage="prune",
                index=j,
                total=len(planned.prune_remotes),
                name=remote,
                verb="Removing",
            )
        )
        r = run_mpremote(planned.port, "rm", f":{remote}")
        if r.returncode != 0:
            log(f"WARN: could not remove :{remote}")
            if r.stderr:
                log(r.stderr.strip())
        else:
            log(f"OK: removed :{remote}")


def _reset_and_wait(log: ProgressLog, port: str) -> None:
    log(stage_header("reset", "soft-reset device"))
    r = run_mpremote(port, "reset")
    log("reset: " + ("ok" if r.returncode == 0 else "warn"))
    log(stage_header("wait-port", f"waiting for {port} after reset (up to 30s)"))
    wait_start = time.monotonic()
    deadline = wait_start + 30.0
    next_tick = wait_start + 5.0
    while time.monotonic() < deadline:
        now = time.monotonic()
        if now >= next_tick:
            log(f"PROGRESS [wait-port] t={int(now - wait_start)}s still waiting for {port}…")
            next_tick += 5.0
        if port_is_listed(port):
            time.sleep(0.5)
            log(f"OK: port {port} back")
            return
        time.sleep(0.25)
    log(f"WARN: port {port} did not reappear within 30s; verify may fail.")


def _verify_identity(
    log: ProgressLog,
    port: str,
    *,
    expect_name: str | None,
    expect_version: str | None,
) -> bool:
    # Same identity grammar as language=c (fw_name=… fw_version=…).
    log(stage_header("verify", "identity on device"))
    code = (
        "import version\n"
        "print('fw_name=%s fw_version=%s' % (version.FW_NAME, version.FW_VERSION))\n"
    )
    r = exec_on_device(port, code)
    if r.returncode != 0:
        time.sleep(1.0)
        r = exec_on_device(port, code)
    if r.returncode != 0:
        log("FAIL: version verify (import version failed)")
        if r.stderr:
            log(r.stderr.strip())
        return False
    blob = (r.stdout or "").strip()
    log("Device reported: " + " ".join(blob.splitlines()))
    got = parse_identity_blob(blob)
    if got is None or not got.complete:
        log("FAIL: could not parse identity line from device")
        return False
    fails = match_expected(got, expect_name=expect_name, expect_version=expect_version)
    if fails:
        log.extend(fails)
        return False
    log("OK: version verify")
    return True


def _verify_import(log: ProgressLog, port: str, verify_import: str) -> bool:
    mod = _safe_module_name(verify_import)
    if not mod:
        log(f"FAIL: --verify-import {verify_import!r} is not a simple module name")
        return False
    code, mode = device_verify_import_snippet(mod)
    log(stage_header("verify-import", f"{mode} {mod}"))
    r = exec_on_device(port, code)
    if r.returncode != 0:
        log(f"FAIL: {mode} verify for {mod!r}")
        if r.stderr:
            log(r.stderr.strip())
        if mode == "compile":
            log(
                "Hint: boot modules are compile-checked (not imported) so the app loop cannot hang deploy."
            )
        return False
    log(f"OK: {mode} verify {mod}")
    return True


def deploy(
    files: list[Path] | None,
    *,
    port: str | None = None,
    yes: bool = False,
    verify: bool = False,
    verify_import: str | None = None,
    expect_name: str | None = None,
    expect_version: str | None = None,
    reset: bool = False,
    prune: bool = False,
    root: Path | None = None,
    on_progress: ProgressCallback | None = None,
) -> DeployResult:
    root = root or Path.cwd()
    cfg = resolve_runtime(root)
    kind = backend_kind(cfg)
    if kind == BACKEND_INVALID:
        return DeployResult(False, list(cfg.errors) or ["FAIL: invalid runtime config"])
    if kind == BACKEND_IDF:
        if verify_import:
            return DeployResult(
                False,
                [
                    "FAIL: --verify-import is MicroPython-only. "
                    "Use --verify for serial identity on C images."
                ],
            )
        if prune:
            return DeployResult(
                False,
                ["FAIL: --prune is MicroPython-only for language=c deploys."],
            )
        return deploy_idf(
            port=port,
            yes=yes,
            verify=verify,
            expect_name=expect_name,
            expect_version=expect_version,
            root=root,
        )

    log = ProgressLog(on_progress)
    planned = plan_deploy(files, port=port, prune=prune, root=root)
    if isinstance(planned, DeployResult):
        log.extend(planned.lines)
        return DeployResult(planned.ok, log.lines)

    log.extend(planned.lines)

    if not yes:
        log("ABORTED: pass --yes only after the operator explicitly confirmed the write.")
        return DeployResult(False, log.lines)

    if not port_is_listed(planned.port):
        log(f"FAIL: port {planned.port} disappeared before write. Re-discover and re-confirm.")
        return DeployResult(False, log.lines)

    if not _write_files(log, planned):
        return DeployResult(False, log.lines)

    _prune_files(log, planned)

    if reset:
        _reset_and_wait(log, planned.port)

    if verify and not _verify_identity(
        log,
        planned.port,
        expect_name=expect_name,
        expect_version=expect_version,
    ):
        return DeployResult(False, log.lines)

    if verify_import and not _verify_import(log, planned.port, verify_import):
        return DeployResult(False, log.lines)

    if verify or verify_import:
        log(
            "INFO: deploy verify talks over the REPL and parks the app loop. "
            "Soft-reset once more (or power cycle) so main.py runs as the product. "
            "Prefer including --reset on write, then soft-reset again after verify if the product face is dead."
        )
        log(
            "If cp/inspect failed with 'could not enter raw repl': the app owns CDC "
            "(Ctrl-C is data). Open the product protocol door (`repl`) or catch the "
            "boot window, then redeploy."
        )

    log(stage_header("done", "deploy finished OK"))
    return DeployResult(True, log.lines)
