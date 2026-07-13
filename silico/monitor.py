"""Read-only CDC stream (does not send Ctrl-C if possible)."""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field

from silico.ports import pick_best_port, port_is_listed


@dataclass
class MonitorResult:
    ok: bool
    lines: list[str] = field(default_factory=list)


def monitor_port(
    *,
    port: str | None = None,
    duration_s: float = 10.0,
    baud: int = 115200,
) -> MonitorResult:
    """Open serial read-only and print bytes for duration_s."""
    try:
        import serial
    except ImportError:
        return MonitorResult(
            False,
            ["FAIL: pyserial not installed (required for silico monitor)"],
        )

    chosen = pick_best_port(port)
    if chosen is None:
        return MonitorResult(False, ["FAIL: no preferred port; pass --port"])
    if port and not port_is_listed(chosen.device):
        return MonitorResult(False, [f"FAIL: {chosen.device} not in inventory"])

    lines = [
        f"Monitoring {chosen.device} read-only for {duration_s}s (baud={baud}).",
        "Does not send Ctrl-C; app should keep running if already looped.",
        "---",
    ]
    try:
        ser = serial.Serial(chosen.device, baudrate=baud, timeout=0.2)
    except Exception as e:
        # Windows re-enum: retry briefly
        deadline = time.monotonic() + 15.0
        ser = None
        last_err = e
        while time.monotonic() < deadline:
            time.sleep(0.5)
            try:
                ser = serial.Serial(chosen.device, baudrate=baud, timeout=0.2)
                break
            except Exception as e2:
                last_err = e2
        if ser is None:
            return MonitorResult(
                False,
                lines
                + [
                    f"FAIL: open {chosen.device}: {last_err}",
                    "What to do next: wait after reset; re-run wait-device; pass explicit --port.",
                ],
            )

    end = time.monotonic() + float(duration_s)
    chunks: list[str] = []
    try:
        while time.monotonic() < end:
            data = ser.read(256)
            if data:
                text = data.decode("utf-8", errors="replace")
                chunks.append(text)
                sys.stdout.write(text)
                sys.stdout.flush()
            else:
                time.sleep(0.05)
    finally:
        ser.close()
    lines.append("---")
    if not chunks:
        lines.append("INFO: no CDC output in window (app silent, wrong port, or still booting)")
    else:
        lines.append(f"OK: captured {sum(len(c) for c in chunks)} chars")
    return MonitorResult(True, lines)
