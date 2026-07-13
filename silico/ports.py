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
VID_CH340 = 0x1A86


@dataclass(frozen=True)
class PortInfo:
    device: str
    vid: int | None
    pid: int | None
    description: str
    manufacturer: str
    score: int
    label: str  # plain-language for operators


def _score(vid: int | None, pid: int | None) -> tuple[int, str]:
    if vid is None:
        return 0, "unknown serial device"
    if vid == VID_RP2 and pid == PID_DEBUG_PROBE:
        return -50, "likely Raspberry Pi Debug Probe (not the app board)"
    if vid == VID_RP2:
        return 100, "likely RP2040 / MicroPython board (prefer this)"
    if vid == VID_CH340:
        return -20, "likely CH340 adapter (often not the XIAO)"
    return 10, "other USB serial"


def list_scored_ports() -> list[PortInfo]:
    if list_ports is None:
        return []
    out: list[PortInfo] = []
    for p in list_ports.comports():
        score, label = _score(p.vid, p.pid)
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


def pick_best_port(explicit: str | None = None) -> PortInfo | None:
    """Return explicit port if given (must exist), else highest-scoring candidate."""
    ports = list_scored_ports()
    if explicit:
        for p in ports:
            if p.device.upper() == explicit.upper() or p.device == explicit:
                return p
        # Explicit may still be valid if list_ports missed it
        return PortInfo(
            device=explicit,
            vid=None,
            pid=None,
            description="",
            manufacturer="",
            score=0,
            label="explicit port (not auto-scored)",
        )
    if not ports:
        return None
    best = ports[0]
    if best.score < 50:
        return None  # refuse blind pick of CH340-only benches
    return best
