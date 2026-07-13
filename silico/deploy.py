"""Deploy application files with explicit confirmation and optional version verify."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from silico.mpremote_util import cp_to_device, exec_on_device, mpremote_available, run_mpremote
from silico.ports import IDENTITY_HINT, pick_best_port, port_is_listed


@dataclass
class DeployPlan:
    port: str
    files: list[tuple[Path, str]]  # local path, remote name
    lines: list[str] = field(default_factory=list)


@dataclass
class DeployResult:
    ok: bool
    lines: list[str] = field(default_factory=list)


def plan_deploy(
    files: list[Path],
    *,
    port: str | None = None,
    remote_names: list[str] | None = None,
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

    if not files:
        return DeployResult(False, ["FAIL: no files to deploy"])

    pairs: list[tuple[Path, str]] = []
    lines = [
        f"Planned write to {chosen.device} ({chosen.label}):",
        "This will OVERWRITE files on the device and may change boot behavior.",
        IDENTITY_HINT,
    ]
    for i, f in enumerate(files):
        path = Path(f)
        if not path.is_file():
            return DeployResult(False, [f"FAIL: not a file: {path}"])
        remote = remote_names[i] if remote_names and i < len(remote_names) else path.name
        pairs.append((path, remote))
        lines.append(f"  {path}  ->  :{remote}")

    lines.append("Refusing to write without explicit confirmation (--yes).")
    lines.append(
        "Operator must have confirmed BOTH: (1) this port is the product board, "
        "(2) these files may be written."
    )
    lines.append("Inspect first: silico inspect --port " + chosen.device)
    return DeployPlan(port=chosen.device, files=pairs, lines=lines)


def deploy(
    files: list[Path],
    *,
    port: str | None = None,
    yes: bool = False,
    verify: bool = False,
    expect_name: str | None = None,
    expect_version: str | None = None,
    reset: bool = False,
) -> DeployResult:
    planned = plan_deploy(files, port=port)
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

    if reset:
        r = run_mpremote(planned.port, "reset")
        lines.append("reset: " + ("ok" if r.returncode == 0 else "warn"))

    if verify:
        code = "import version\nprint(version.FW_NAME)\nprint(version.FW_VERSION)\n"
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

    return DeployResult(True, lines)
