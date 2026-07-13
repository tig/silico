"""Poll USB serial until a preferred board appears (do not make humans announce plug-in)."""

from __future__ import annotations

import time

from silico.ports import PortInfo, list_scored_ports


def wait_for_board(
    *,
    timeout_s: float = 60.0,
    poll_s: float = 1.0,
    min_score: int = 50,
) -> PortInfo | None:
    """Poll until a port with score >= min_score appears, or timeout."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        ports = list_scored_ports()
        for p in ports:
            if p.score >= min_score:
                return p
        time.sleep(poll_s)
    return None
