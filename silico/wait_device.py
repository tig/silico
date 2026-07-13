"""Poll USB serial until a preferred board appears (do not make humans announce plug-in)."""

from __future__ import annotations

import time
from collections.abc import Callable

from silico.ports import PortInfo, list_scored_ports


def wait_for_board(
    *,
    timeout_s: float = 180.0,
    poll_s: float = 2.0,
    min_score: int = 50,
    on_poll: Callable[[float, list[PortInfo]], None] | None = None,
) -> PortInfo | None:
    """Poll until a port with score >= min_score appears, or timeout.

    on_poll(elapsed_s, ports) is called each iteration so agents can narrate
    without asking the human to announce plug-in.
    """
    start = time.monotonic()
    deadline = start + timeout_s
    while True:
        now = time.monotonic()
        ports = list_scored_ports()
        if on_poll is not None:
            on_poll(now - start, ports)
        for p in ports:
            if p.score >= min_score:
                return p
        if now >= deadline:
            return None
        time.sleep(min(poll_s, max(0.0, deadline - time.monotonic())))


def format_port_snapshot(ports: list[PortInfo]) -> str:
    if not ports:
        return "(no serial ports)"
    parts = []
    for p in ports:
        vid = f"{p.vid:04x}" if p.vid is not None else "----"
        pid = f"{p.pid:04x}" if p.pid is not None else "----"
        parts.append(f"{p.device}[{vid}:{pid} score={p.score}]")
    return ", ".join(parts)


TIMEOUT_SOP = [
    "TIMEOUT: no preferred board (score>=50) appeared.",
    "Agent SOP (do not ask the human to announce plug-in):",
    "  1. Ask only for a physical step if needed: data USB cable (not charge-only), plug into the PC.",
    "  2. Extend the poll: silico wait-device --timeout 300",
    "  3. On appear: silico doctor && silico inspect --port COMx",
    "  4. Report findings; CONFIRM with operator that this is the product board before any deploy plan.",
    "  5. If still nothing: BOOT+RESET UF2 path (RPI-RP2) for first MicroPython flash - once per board.",
]
