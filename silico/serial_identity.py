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


def probe_serial_identity(
    port: str,
    *,
    baud: int = 115200,
    listen_s: float = 2.0,
    reset: bool = True,
    knock: bool = True,
    expect_name: str | None = None,
    expect_version: str | None = None,
) -> SerialIdentityResult:
    """Open *port*, optional DTR/RTS pulse, knock ``identity``, parse response.

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
        ser.dtr = False
        ser.rts = False
        ser.open()
    except Exception as e:  # noqa: BLE001
        return SerialIdentityResult(False, [f"FAIL: open {port}: {e}"])

    try:
        if reset:
            lines.append("Pulse DTR/RTS (best-effort reset)...")
            _pulse_reset(ser)
        ser.reset_input_buffer()
        if knock:
            lines.append("Knock: CR/LF + identity")
            ser.write(b"\r\n")
            time.sleep(0.15)
            ser.write(b"identity\r\n")
            time.sleep(0.1)
        buf = bytearray()
        t0 = time.time()
        while time.time() - t0 < listen_s:
            chunk = ser.read(512)
            if chunk:
                buf.extend(chunk)
        raw = bytes(buf)
    finally:
        ser.close()

    lines.append(f"Captured {len(raw)} bytes @ {baud}")
    if raw:
        preview = raw[:160]
        lines.append(f"  raw: {preview!r}{'…' if len(raw) > 160 else ''}")

    text = raw.decode("utf-8", errors="replace")
    got = parse_identity_blob(text)
    if got is None or not (got.fw_name or got.fw_version):
        lines.append("RESULT: no identity line found on serial")
        lines.append(
            "C images must print fw_name=… fw_version=… on boot or answer identity."
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
