"""Serial identity knock for non-MicroPython images (C / ESP-IDF)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from silico.identity import Identity, match_expected, parse_identity_blob


@dataclass
class SerialIdentityResult:
    ok: bool
    lines: list[str] = field(default_factory=list)
    identity: Identity | None = None
    raw: bytes = b""


def _pulse_reset(ser) -> None:
    """Toggle DTR/RTS like a USB-UART reset (can land CH9102 in download/ROM)."""
    try:
        ser.dtr = False
        ser.rts = True
        time.sleep(0.05)
        ser.dtr = True
        ser.rts = False
        time.sleep(0.05)
        ser.dtr = False
        time.sleep(0.1)
    except Exception:  # noqa: BLE001
        pass


def _hold_deasserted(ser) -> None:
    """Keep control lines idle so the app keeps running (CH9102 / M5GO-safe)."""
    try:
        ser.dtr = False
        ser.rts = False
    except Exception:  # noqa: BLE001
        pass


def _knock(ser) -> None:
    ser.write(b"\r\n")
    time.sleep(0.15)
    ser.write(b"identity\r\n")
    time.sleep(0.1)


def _listen(ser, listen_s: float) -> bytes:
    buf = bytearray()
    t0 = time.time()
    while time.time() - t0 < listen_s:
        chunk = ser.read(512)
        if chunk:
            buf.extend(chunk)
    return bytes(buf)


def probe_serial_identity(
    port: str,
    *,
    baud: int = 115200,
    listen_s: float = 3.0,
    boot_wait_s: float = 1.5,
    reset: bool = False,
    knock: bool = True,
    expect_name: str | None = None,
    expect_version: str | None = None,
) -> SerialIdentityResult:
    """Open *port*, knock ``identity``, parse response.

    Default: DTR/RTS **deasserted**, **no** reset pulse, then knock (tig/silico#78).
    CH9102/M5GO: a best-effort DTR/RTS pulse often lands ROM/download so the app
    never answers; bare pyserial with dtr=rts=False works. Pass ``reset=True`` only
    when you intentionally want a pulse + boot wait (e.g. boot-greeting capture).

    Does not use mpremote. Never writes firmware.
    """
    lines: list[str] = []
    try:
        import serial
    except ImportError:
        return SerialIdentityResult(
            False, ["FAIL: pyserial not installed (pip install pyserial)"]
        )

    try:
        ser = serial.Serial()
        ser.port = port
        ser.baudrate = baud
        ser.timeout = 0.05
        ser.write_timeout = 1.0
        # Set before open so Windows does not leave lines asserted after open.
        ser.dtr = False
        ser.rts = False
        ser.open()
        _hold_deasserted(ser)
    except Exception as e:  # noqa: BLE001
        return SerialIdentityResult(False, [f"FAIL: open {port}: {e}"])

    raw = b""
    try:
        _hold_deasserted(ser)
        if reset:
            lines.append("Pulse DTR/RTS (best-effort reset)...")
            _pulse_reset(ser)
            _hold_deasserted(ser)
            if boot_wait_s > 0:
                lines.append(f"Wait {boot_wait_s:g}s for app boot after pulse...")
                time.sleep(boot_wait_s)
        else:
            lines.append("Lines held deasserted (no DTR/RTS pulse; CH9102-safe)")
        try:
            ser.reset_input_buffer()
        except Exception:  # noqa: BLE001
            pass
        if knock:
            lines.append("Knock: CR/LF + identity")
            try:
                _knock(ser)
            except Exception as e:  # noqa: BLE001
                lines.append(f"WARN: knock write failed: {e}")
        raw = _listen(ser, listen_s)
    finally:
        try:
            ser.close()
        except Exception:  # noqa: BLE001
            pass

    lines.append(f"Captured {len(raw)} bytes @ {baud}")
    if raw:
        preview = raw[:160]
        lines.append(f"  raw: {preview!r}{'...' if len(raw) > 160 else ''}")

    text = raw.decode("utf-8", errors="replace")
    got = parse_identity_blob(text)
    if got is None or not (got.fw_name or got.fw_version):
        lines.append("RESULT: no identity line found on serial")
        lines.append(
            "C images must print fw_name=... fw_version=... on boot or answer identity."
        )
        lines.append(
            "Hint: CH9102/M5GO — keep default (no DTR/RTS pulse). "
            "Manual: open COM with dtr=rts=False, write identity + newline."
        )
        return SerialIdentityResult(False, lines, identity=None, raw=raw)

    lines.append(
        f"RESULT: identity fw_name={got.fw_name!r} fw_version={got.fw_version!r}"
    )
    if got.raw_line:
        lines.append(f"  from: {got.raw_line!r}")
    fails = match_expected(
        got, expect_name=expect_name, expect_version=expect_version
    )
    if fails:
        lines.extend(fails)
        return SerialIdentityResult(False, lines, identity=got, raw=raw)
    if expect_name or expect_version:
        lines.append("OK: identity matches expected")
    else:
        lines.append("OK: identity present")
    return SerialIdentityResult(True, lines, identity=got, raw=raw)
