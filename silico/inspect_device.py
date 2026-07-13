"""Non-destructive device inspection (never writes)."""

from __future__ import annotations

from dataclasses import dataclass, field

from silico.mpremote_util import exec_on_device, ls_device, mpremote_available
from silico.ports import IDENTITY_HINT, pick_best_port, port_is_listed


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
    lines.append("REPL:")
    lines.append((r.stdout or "").strip() or "(no output)")

    ls = ls_device(p)
    if ls.returncode == 0:
        lines.append("Files on device:")
        lines.append((ls.stdout or "").strip() or "(empty)")
    else:
        lines.append("WARN: could not list device files")

    ver = exec_on_device(
        p,
        "try:\n import version\n print(version.FW_NAME, getattr(version,'FW_VERSION', '?'))\nexcept Exception as e:\n print('no version module:', type(e).__name__)",
    )
    if ver.returncode == 0:
        lines.append("Version probe: " + (ver.stdout or "").strip())

    lines.append("Read-only inspect complete. No files were written.")
    lines.append(IDENTITY_HINT)
    return InspectReport(True, p, lines)
