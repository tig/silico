"""Non-destructive device inspection (never writes)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from silico.config_toml import read_deploy_core, read_product_identity
from silico.mpy_pin import (
    apply_mpy_cross_pin,
    parse_micropython_version,
    pin_advice_lines,
    read_toml_mpy_cross,
)
from silico.mpremote_util import exec_on_device, ls_device, mpremote_available
from silico.ports import IDENTITY_HINT, pick_best_port, port_is_listed
from silico.pull_device import _parse_ls_names
from silico.runtime import resolve_runtime
from silico.serial_identity import probe_serial_identity


@dataclass
class InspectReport:
    ok: bool
    port: str | None
    lines: list[str] = field(default_factory=list)
    device_mpy: str | None = None


def _resolve_inspect_port(
    port: str | None,
) -> tuple[object, None] | tuple[None, InspectReport]:
    """Pick and validate port. Returns (PortInfo, None) or (None, fail report)."""
    chosen = pick_best_port(port)
    if chosen is None:
        return None, InspectReport(
            False,
            None,
            [
                "FAIL: no preferred board port found.",
                "Plug a data USB cable and run: silico wait-device",
                "Or pass --port COMx explicitly after operator confirms identity.",
                "Do not use CH340-only benches without --port.",
            ],
        )
    p = chosen.device
    if port and not port_is_listed(p):
        return None, InspectReport(
            False,
            p,
            [
                f"FAIL: --port {p} is not in the current serial inventory.",
                "Device unplugged, wrong COM, or path changed. Re-run: silico wait-device",
                "Do not reuse a COM number from an earlier session without re-discovery.",
            ],
        )
    return chosen, None


def _inspect_c(
    port: str | None,
    *,
    apply_mpy_pin: bool,
    root: Path | None,
) -> InspectReport:
    lines: list[str] = []
    if apply_mpy_pin:
        return InspectReport(
            False,
            None,
            [
                "FAIL: --apply-mpy-pin is MicroPython-only.",
                "language=c pins ESP-IDF from silico.toml ([runtime].esp_idf), not from the device.",
            ],
        )

    cfg = resolve_runtime(root)
    chosen, fail = _resolve_inspect_port(port)
    if fail is not None:
        return fail
    assert chosen is not None
    p = chosen.device

    lines.append(f"Port: {p} ({chosen.label})")
    lines.append(f"Mode: serial identity (language={cfg.language}, no mpremote REPL)")
    name, ver = read_product_identity(root)
    probe = probe_serial_identity(
        p,
        baud=cfg.baud,
        expect_name=name,
        expect_version=ver,
    )
    lines.extend(probe.lines)
    if not probe.ok:
        lines.append(IDENTITY_HINT)
        return InspectReport(False, p, lines)

    lines.append("Read-only inspect complete. No files were written.")
    lines.append(IDENTITY_HINT)
    return InspectReport(True, p, lines)


def inspect(
    port: str | None = None,
    *,
    apply_mpy_pin: bool = False,
    root: Path | None = None,
) -> InspectReport:
    lines: list[str] = []
    root = root or Path.cwd()
    cfg = resolve_runtime(root)

    if cfg.language == "c":
        return _inspect_c(port, apply_mpy_pin=apply_mpy_pin, root=root)

    # --apply-mpy-pin mutates the product repo (silico.toml, requirements-dev.txt).
    # Auto-selection scores ports by preference; a high score is a hint, not an
    # identification. On a bench with two RP2040s that hint can pin the repo to
    # the wrong board's ABI. Reading is allowed to guess; writing is not.
    # Checked before mpremote so it is argument validation, not a tooling probe.
    if apply_mpy_pin and not port:
        return InspectReport(
            False,
            None,
            [
                "FAIL: --apply-mpy-pin requires an explicit --port.",
                "It writes silico.toml and requirements-dev.txt, so the board must be",
                "identified by the operator, not guessed from port scoring.",
                "Run `silico inspect` (read-only) first to see candidates, then:",
                "  silico inspect --port COMx --apply-mpy-pin",
            ],
        )

    if not mpremote_available():
        return InspectReport(False, None, ["FAIL: mpremote not available"])

    chosen, fail = _resolve_inspect_port(port)
    if fail is not None:
        return fail
    assert chosen is not None
    p = chosen.device

    lines.append(f"Port: {p} ({chosen.label})")
    # Prefer implementation.version for ABI; language version alone misleads (UIFlow).
    r = exec_on_device(
        p,
        "import sys\n"
        "print(sys.platform)\n"
        "print(sys.implementation)\n"
        "print(sys.version)\n",
    )
    if r.returncode != 0:
        lines.append("FAIL: could not talk to device (unplugged, wrong port, or held by another program)")
        if r.stderr:
            lines.append(r.stderr.strip())
        # stderr may already include LOCKOUT_RECOVERY from run_mpremote (#49/#62).
        err_l = (r.stderr or "").lower()
        if "lockout" not in err_l and "erase-flash" not in err_l and "owns the console" not in err_l:
            from silico.mpremote_util import LOCKOUT_RECOVERY

            lines.append(LOCKOUT_RECOVERY)
        return InspectReport(False, p, lines)
    repl_out = (r.stdout or "").strip() or "(no output)"
    lines.append("REPL:")
    lines.append(repl_out)

    ls = ls_device(p)
    if ls.returncode == 0:
        lines.append("Files on device:")
        lines.append((ls.stdout or "").strip() or "(empty)")
        core = read_deploy_core(root)
        if core:
            want = {Path(c).name for c in core}
            on_dev = set(_parse_ls_names(ls.stdout or ""))
            orphans = sorted(n for n in on_dev if n.endswith(".py") and n not in want)
            missing = sorted(n for n in want if n not in on_dev)
            if orphans:
                lines.append("WARN: on device but not in [deploy].core:")
                for n in orphans:
                    lines.append(f"  :{n}")
            if missing:
                lines.append("INFO: in [deploy].core but not on device yet:")
                for n in missing:
                    lines.append(f"  :{n}")
    else:
        lines.append("WARN: could not list device files")

    ver = exec_on_device(
        p,
        "try:\n import version\n print(version.FW_NAME, getattr(version,'FW_VERSION', '?'))\nexcept Exception as e:\n print('no version module:', type(e).__name__)",
    )
    if ver.returncode == 0:
        lines.append("Version probe: " + (ver.stdout or "").strip())

    # mpy-cross pin vs device MicroPython (host gate ABI)
    device_mpy = parse_micropython_version(repl_out)
    toml_pin = read_toml_mpy_cross(root)
    lines.append("mpy-cross pin check:")
    for line in pin_advice_lines(repl_out, toml_pin):
        lines.append("  " + line)

    if apply_mpy_pin:
        if not device_mpy:
            lines.append(
                "FAIL: --apply-mpy-pin needs a parseable MicroPython version from REPL"
            )
            lines.append(IDENTITY_HINT)
            return InspectReport(False, p, lines, device_mpy=None)
        from silico.mpy_pin import is_ancient_micropython

        if is_ancient_micropython(device_mpy):
            lines.append(
                "FAIL: refusing --apply-mpy-pin on ancient MicroPython "
                f"({device_mpy}). First-flash a current port build, then re-inspect."
            )
            lines.append(IDENTITY_HINT)
            return InspectReport(False, p, lines, device_mpy=device_mpy)
        lines.append("Applying mpy-cross pin on host (device not written):")
        for line in apply_mpy_cross_pin(device_mpy, root=root):
            lines.append("  " + line)
        lines.append("Inspect complete. Host pin files updated; device unchanged.")
    else:
        lines.append("Read-only inspect complete. No files were written.")
        if device_mpy:
            lines.append(
                "To own the ABI pin (toml + requirements-dev): "
                "silico inspect --port … --apply-mpy-pin"
            )
    lines.append(IDENTITY_HINT)
    return InspectReport(True, p, lines, device_mpy=device_mpy)
