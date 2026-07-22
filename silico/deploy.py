"""Deploy application files with explicit confirmation and optional version verify."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
import time
from pathlib import Path

from silico.config_toml import read_deploy_core
from silico.mpremote_util import cp_to_device, exec_on_device, ls_device, mpremote_available, run_mpremote
from silico.ports import IDENTITY_HINT, pick_best_port, port_is_listed
from silico.progress import (
    ProgressCallback,
    emit,
    file_size,
    file_step,
    format_bytes,
    stage_header,
)
from silico.pull_device import _parse_ls_names


@dataclass
class DeployPlan:
    port: str
    files: list[tuple[Path, str]]  # local path, remote name
    lines: list[str] = field(default_factory=list)
    prune_remotes: list[str] = field(default_factory=list)


@dataclass
class DeployResult:
    ok: bool
    lines: list[str] = field(default_factory=list)



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
        # open+compile; do not exec / import the boot module
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
                '  [deploy]',
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
            # Never auto-delete unknown system leftovers without listing
            prune_remotes = sorted(n for n in on_dev if n.endswith(".py") and n not in want)
            if prune_remotes:
                lines.append("Will REMOVE on device (--prune), .py not in manifest:")
                for n in prune_remotes:
                    lines.append(f"  delete :{n}")
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
    )


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
    planned = plan_deploy(files, port=port, prune=prune, root=root)
    if isinstance(planned, DeployResult):
        if on_progress:
            for line in planned.lines:
                on_progress(line)
        return planned

    lines: list[str] = []
    for line in planned.lines:
        emit(lines, line, on_progress=on_progress)

    if not yes:
        emit(
            lines,
            "ABORTED: pass --yes only after the operator explicitly confirmed the write.",
            on_progress=on_progress,
        )
        return DeployResult(False, lines)

    if not port_is_listed(planned.port):
        emit(
            lines,
            f"FAIL: port {planned.port} disappeared before write. Re-discover and re-confirm.",
            on_progress=on_progress,
        )
        return DeployResult(False, lines)

    n = len(planned.files)
    total_b = sum(max(file_size(p), 0) for p, _ in planned.files)
    emit(
        lines,
        stage_header(
            "write",
            f"Confirmed (--yes). Copying {n} file(s), {format_bytes(total_b)} via mpremote…",
        ),
        on_progress=on_progress,
    )
    for i, (local, remote) in enumerate(planned.files, start=1):
        sz = file_size(local)
        emit(
            lines,
            file_step(stage="write", index=i, total=n, name=remote, size=sz, verb="Writing"),
            on_progress=on_progress,
        )
        # Scale timeout for larger assets (audio riffs, etc.)
        timeout = 30.0
        if sz > 0:
            timeout = max(30.0, min(600.0, 30.0 + sz / 50_000.0))
        t0 = time.monotonic()
        r = cp_to_device(planned.port, local, remote, timeout=timeout)
        elapsed = time.monotonic() - t0
        if r.returncode != 0:
            emit(lines, f"FAIL: cp {local} -> :{remote}", on_progress=on_progress)
            if r.stderr:
                emit(lines, r.stderr.strip(), on_progress=on_progress)
            return DeployResult(False, lines)
        emit(
            lines,
            f"OK: wrote :{remote} ({format_bytes(sz) if sz >= 0 else '?'}) in {elapsed:.1f}s",
            on_progress=on_progress,
        )

    if planned.prune_remotes:
        emit(
            lines,
            stage_header("prune", f"{len(planned.prune_remotes)} orphan .py"),
            on_progress=on_progress,
        )
    for j, remote in enumerate(planned.prune_remotes, start=1):
        emit(
            lines,
            file_step(
                stage="prune",
                index=j,
                total=len(planned.prune_remotes),
                name=remote,
                verb="Removing",
            ),
            on_progress=on_progress,
        )
        r = run_mpremote(planned.port, "rm", f":{remote}")
        if r.returncode != 0:
            emit(lines, f"WARN: could not remove :{remote}", on_progress=on_progress)
            if r.stderr:
                emit(lines, r.stderr.strip(), on_progress=on_progress)
        else:
            emit(lines, f"OK: removed :{remote}", on_progress=on_progress)

    if reset:
        emit(lines, stage_header("reset", "soft-reset device"), on_progress=on_progress)
        r = run_mpremote(planned.port, "reset")
        emit(
            lines,
            "reset: " + ("ok" if r.returncode == 0 else "warn"),
            on_progress=on_progress,
        )
        emit(
            lines,
            stage_header("wait-port", f"waiting for {planned.port} after reset (up to 30s)"),
            on_progress=on_progress,
        )
        wait_start = time.monotonic()
        deadline = wait_start + 30.0
        last_tick = -1
        while time.monotonic() < deadline:
            elapsed = int(time.monotonic() - wait_start)
            if elapsed >= 5 and elapsed // 5 != last_tick // 5:
                emit(
                    lines,
                    f"PROGRESS [wait-port] t={elapsed}s still waiting for {planned.port}…",
                    on_progress=on_progress,
                )
                last_tick = elapsed
            if port_is_listed(planned.port):
                time.sleep(0.5)
                emit(lines, f"OK: port {planned.port} back", on_progress=on_progress)
                break
            time.sleep(0.25)
        else:
            emit(
                lines,
                f"WARN: port {planned.port} did not reappear within 30s; verify may fail.",
                on_progress=on_progress,
            )

    if verify:
        emit(lines, stage_header("verify", "import version on device"), on_progress=on_progress)
        code = "import version\nprint(version.FW_NAME)\nprint(version.FW_VERSION)\n"
        r = exec_on_device(planned.port, code)
        if r.returncode != 0:
            time.sleep(1.0)
            r = exec_on_device(planned.port, code)
        if r.returncode != 0:
            emit(lines, "FAIL: version verify (import version failed)", on_progress=on_progress)
            if r.stderr:
                emit(lines, r.stderr.strip(), on_progress=on_progress)
            return DeployResult(False, lines)
        out = (r.stdout or "").strip().splitlines()
        emit(lines, "Device reported: " + " ".join(out), on_progress=on_progress)
        got_name = out[0].strip() if out else None
        got_version = out[1].strip() if len(out) > 1 else None
        if expect_name and got_name != expect_name:
            emit(
                lines,
                f"FAIL: FW_NAME want {expect_name!r} got {got_name!r}",
                on_progress=on_progress,
            )
            return DeployResult(False, lines)
        if expect_version and got_version != expect_version:
            emit(
                lines,
                f"FAIL: FW_VERSION want {expect_version!r} got {got_version!r}",
                on_progress=on_progress,
            )
            return DeployResult(False, lines)
        emit(lines, "OK: version verify", on_progress=on_progress)

    # Optional soft liveness: import module, or compile-check boot entrypoints
    if verify_import:
        mod = _safe_module_name(verify_import)
        if not mod:
            emit(
                lines,
                f"FAIL: --verify-import {verify_import!r} is not a simple module name",
                on_progress=on_progress,
            )
            return DeployResult(False, lines)
        code, mode = device_verify_import_snippet(mod)
        emit(
            lines,
            stage_header("verify-import", f"{mode} {mod}"),
            on_progress=on_progress,
        )
        r = exec_on_device(planned.port, code)
        if r.returncode != 0:
            emit(lines, f"FAIL: {mode} verify for {mod!r}", on_progress=on_progress)
            if r.stderr:
                emit(lines, r.stderr.strip(), on_progress=on_progress)
            if mode == "compile":
                emit(
                    lines,
                    "Hint: boot modules are compile-checked (not imported) so the app loop cannot hang deploy.",
                    on_progress=on_progress,
                )
            return DeployResult(False, lines)
        emit(lines, f"OK: {mode} verify {mod}", on_progress=on_progress)

    # Only when we entered the REPL for verification — avoid nagging on plain --yes writes.
    if verify or verify_import:
        emit(
            lines,
            "INFO: deploy verify talks over the REPL and parks the app loop. "
            "Soft-reset once more (or power cycle) so main.py runs as the product. "
            "Prefer including --reset on write, then soft-reset again after verify if the product face is dead.",
            on_progress=on_progress,
        )
        emit(
            lines,
            "If cp/inspect failed with 'could not enter raw repl': the app owns CDC "
            "(Ctrl-C is data). Open the product protocol door (`repl`) or catch the "
            "boot window, then redeploy.",
            on_progress=on_progress,
        )

    emit(lines, stage_header("done", "deploy finished OK"), on_progress=on_progress)
    return DeployResult(True, lines)
