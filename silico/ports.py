"""Serial port discovery and scoring (host only)."""

from __future__ import annotations

from dataclasses import dataclass

try:
    from serial.tools import list_ports
except ImportError:  # pragma: no cover
    list_ports = None  # type: ignore


# Prefer MicroPython / RP2040 CDC; demote common hazards.
VID_RP2 = 0x2E8A
PID_DEBUG_PROBE = 0x000C
VID_WCH = 0x1A86  # WCH USB-serial family (CH340, CH9102, …)
PID_CH340 = 0x7523
PID_CH9102 = 0x55D4
# Silicon Labs CP210x — common ESP / M5-class boards
VID_SILABS = 0x10C4
# Espressif USB JTAG/serial (some S2/S3 boards)
VID_ESPRESSIF = 0x303A


@dataclass(frozen=True)
class PortInfo:
    device: str
    vid: int | None
    pid: int | None
    description: str
    manufacturer: str
    score: int
    label: str  # plain-language for operators


def _score(
    vid: int | None,
    pid: int | None,
    *,
    description: str = "",
) -> tuple[int, str]:
    """Score a USB serial candidate.

    Higher is better. score>=50 may be auto-preferred by wait-device / pick_best.
    Always confirm board identity with the operator before deploy.
    """
    desc = (description or "").upper()
    if vid is None:
        return 0, "unknown serial device"

    if vid == VID_RP2 and pid == PID_DEBUG_PROBE:
        return -50, "likely Raspberry Pi Debug Probe (not the app board)"
    if vid == VID_RP2:
        return 100, "likely RP2040 / MicroPython board (prefer this)"

    # WCH family: do not treat all 1a86 as CH340
    if vid == VID_WCH:
        if pid == PID_CH9102 or "CH9102" in desc:
            return 55, "USB-serial candidate (CH9102 / ESP-class CDC) — confirm board"
        if pid == PID_CH340 or "CH340" in desc:
            return -20, "likely CH340 adapter (often not the product board)"
        return 40, "WCH USB-serial candidate — confirm board (not all are CH340)"

    if vid == VID_SILABS or "CP210" in desc:
        return 50, "USB-serial candidate (CP210x / ESP-class) — confirm board"

    if vid == VID_ESPRESSIF:
        return 60, "likely Espressif USB serial — confirm board"

    return 10, "other USB serial — confirm board"


def list_scored_ports() -> list[PortInfo]:
    if list_ports is None:
        return []
    out: list[PortInfo] = []
    for p in list_ports.comports():
        score, label = _score(p.vid, p.pid, description=p.description or "")
        out.append(
            PortInfo(
                device=p.device,
                vid=p.vid,
                pid=p.pid,
                description=p.description or "",
                manufacturer=p.manufacturer or "",
                score=score,
                label=label,
            )
        )
    out.sort(key=lambda x: (-x.score, x.device))
    return out


def port_is_listed(device: str) -> bool:
    """True if device currently appears in the host serial inventory."""
    want = device.upper()
    for p in list_scored_ports():
        if p.device.upper() == want or p.device == device:
            return True
    return False


def pick_best_port(explicit: str | None = None) -> PortInfo | None:
    """Return explicit port if given, else highest-scoring candidate (score>=50).

    Explicit ports that are not currently listed still return a PortInfo so
    callers can fail with a clear message (deploy/inspect should check listed).
    """
    ports = list_scored_ports()
    if explicit:
        for p in ports:
            if p.device.upper() == explicit.upper() or p.device == explicit:
                return p
        return PortInfo(
            device=explicit,
            vid=None,
            pid=None,
            description="",
            manufacturer="",
            score=0,
            label="explicit port (not currently in serial inventory)",
        )
    if not ports:
        return None
    best = ports[0]
    if best.score < 50:
        return None  # refuse blind pick of low-score-only benches
    return best


IDENTITY_HINT = (
    "CONFIRM WITH OPERATOR: high score is a hint, not proof this is the product board. "
    "Report port + inspect findings; get a clear yes on device identity before deploy."
)
