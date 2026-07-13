"""Non-destructive device inspection (never writes)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from silico.config_toml import read_deploy_core
from silico.mpy_pin import pin_advice_lines, read_toml_mpy_cross
from silico.mpremote_util import exec_on_device, ls_device, mpremote_available
from silico.ports import IDENTITY_HINT, pick_best_port, port_is_listed
from silico.pull_device import _parse_ls_names


@dataclass
class InspectReport:
    ok: bool
    port: str | None
    lines: list[str] = field(default_factory=list)


def inspect(port: str | None = None) -> InspectReport:
    lines: list[str] = []
    if not mpremote_available():
        return InspectReport(False, None, ["FAIL: mpremote not available"])

    chosen = pick_best_port(port)
    if chosen is None:
        return InspectReport(
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
        return InspectReport(
            False,
            p,
            [
                f"FAIL: --port {p} is not in the current serial inventory.",
                "Device unplugged, wrong COM, or path changed. Re-run: silico wait-device",
                "Do not reuse a COM number from an earlier session without re-discovery.",
            ],
        )

    lines.append(f"Port: {p} ({chosen.label})")
    r = exec_on_device(p, "import sys; print(sys.platform); print(sys.version)")
    if r.returncode != 0:
        lines.append("FAIL: could not talk to device (unplugged, wrong port, or held by another program)")
        if r.stderr:
            lines.append(r.stderr.strip())
        return InspectReport(False, p, lines)
    repl_out = (r.stdout or "").strip() or "(no output)"
    lines.append("REPL:")
    lines.append(repl_out)

    ls = ls_device(p)
    if ls.returncode == 0:
        lines.append("Files on device:")
        lines.append((ls.stdout or "").strip() or "(empty)")
        core = read_deploy_core()
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
    toml_pin = read_toml_mpy_cross()
    lines.append("mpy-cross pin check:")
    for line in pin_advice_lines(repl_out, toml_pin):
        lines.append("  " + line)

    lines.append("Read-only inspect complete. No files were written.")
    lines.append(IDENTITY_HINT)
    return InspectReport(True, p, lines)
