"""Deploy application files with explicit confirmation and optional version verify."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from pathlib import Path

from silico.config_toml import read_deploy_core
from silico.mpremote_util import cp_to_device, exec_on_device, ls_device, mpremote_available, run_mpremote
from silico.ports import IDENTITY_HINT, pick_best_port, port_is_listed
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
    lines = [
        f"Planned write to {chosen.device} ({chosen.label}):",
        "This will OVERWRITE files on the device and may change boot behavior.",
        IDENTITY_HINT,
    ]
    if not files:
        lines.append("Using [deploy].core from silico.toml")
    for i, f in enumerate(file_list):
        path = Path(f)
        if not path.is_file():
            return DeployResult(False, [f"FAIL: not a file: {path}"])
        remote = remote_names[i] if remote_names and i < len(remote_names) else path.name
        pairs.append((path, remote))
        lines.append(f"  {path}  ->  :{remote}")

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
) -> DeployResult:
    planned = plan_deploy(files, port=port, prune=prune, root=root)
    if isinstance(planned, DeployResult):
        return planned

    lines = list(planned.lines)
    if not yes:
        lines.append("ABORTED: pass --yes only after the operator explicitly confirmed the write.")
        return DeployResult(False, lines)

    if not port_is_listed(planned.port):
        lines.append(f"FAIL: port {planned.port} disappeared before write. Re-discover and re-confirm.")
        return DeployResult(False, lines)

    lines.append("Confirmed (--yes). Writing...")
    for local, remote in planned.files:
        r = cp_to_device(planned.port, local, remote)
        if r.returncode != 0:
            lines.append(f"FAIL: cp {local} -> :{remote}")
            if r.stderr:
                lines.append(r.stderr.strip())
            return DeployResult(False, lines)
        lines.append(f"OK: wrote :{remote}")

    for remote in planned.prune_remotes:
        r = run_mpremote(planned.port, "rm", f":{remote}")
        if r.returncode != 0:
            lines.append(f"WARN: could not remove :{remote}")
            if r.stderr:
                lines.append(r.stderr.strip())
        else:
            lines.append(f"OK: removed :{remote}")

    if reset:
        r = run_mpremote(planned.port, "reset")
        lines.append("reset: " + ("ok" if r.returncode == 0 else "warn"))
        lines.append("Waiting for port to reappear after reset...")
        import time

        deadline = time.monotonic() + 30.0
        while time.monotonic() < deadline:
            if port_is_listed(planned.port):
                time.sleep(0.5)
                break
            time.sleep(0.25)
        else:
            lines.append(
                f"WARN: port {planned.port} did not reappear within 30s; verify may fail."
            )

    if verify:
        code = "import version\nprint(version.FW_NAME)\nprint(version.FW_VERSION)\n"
        r = exec_on_device(planned.port, code)
        if r.returncode != 0:
            import time

            time.sleep(1.0)
            r = exec_on_device(planned.port, code)
        if r.returncode != 0:
            lines.append("FAIL: version verify (import version failed)")
            if r.stderr:
                lines.append(r.stderr.strip())
            return DeployResult(False, lines)
        out = (r.stdout or "").strip().splitlines()
        lines.append("Device reported: " + " ".join(out))
        got_name = out[0].strip() if out else None
        got_version = out[1].strip() if len(out) > 1 else None
        if expect_name and got_name != expect_name:
            lines.append(f"FAIL: FW_NAME want {expect_name!r} got {got_name!r}")
            return DeployResult(False, lines)
        if expect_version and got_version != expect_version:
            lines.append(f"FAIL: FW_VERSION want {expect_version!r} got {got_version!r}")
            return DeployResult(False, lines)
        lines.append("OK: version verify")

    # Optional soft liveness: import module, or compile-check boot entrypoints
    if verify_import:
        mod = _safe_module_name(verify_import)
        if not mod:
            lines.append(
                f"FAIL: --verify-import {verify_import!r} is not a simple module name"
            )
            return DeployResult(False, lines)
        code, mode = device_verify_import_snippet(mod)
        r = exec_on_device(planned.port, code)
        if r.returncode != 0:
            lines.append(f"FAIL: {mode} verify for {mod!r}")
            if r.stderr:
                lines.append(r.stderr.strip())
            if mode == "compile":
                lines.append(
                    "Hint: boot modules are compile-checked (not imported) so the app loop cannot hang deploy."
                )
            return DeployResult(False, lines)
        lines.append(f"OK: {mode} verify {mod}")

    # Verify uses the raw REPL and parks a running app loop. Agents must leave
    # the device running the product boot entry for "hello metal" proof.
    lines.append(
        "INFO: deploy verify talks over the REPL and parks the app loop. "
        "Soft-reset once more (or power cycle) so main.py runs as the product. "
        "Prefer including --reset on write, then soft-reset again after verify if the face is dead."
    )
    lines.append(
        "If cp/inspect failed with 'could not enter raw repl': the app owns CDC "
        "(Ctrl-C is data). Open the product protocol door (`repl`) or catch the "
        "boot window, then redeploy."
    )

    return DeployResult(True, lines)
