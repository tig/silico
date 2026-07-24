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


def _clear_input(ser) -> None:
    try:
        ser.reset_input_buffer()
    except Exception:  # noqa: BLE001
        pass


def _knock_once(ser) -> None:
    """Single identity knock (CR/LF then ``identity``)."""
    ser.write(b"\r\n")
    time.sleep(0.05)
    ser.write(b"identity\r\n")


def _identity_in_raw(raw: bytes) -> Identity | None:
    text = raw.decode("utf-8", errors="replace")
    got = parse_identity_blob(text)
    if got is None or not (got.fw_name or got.fw_version):
        return None
    return got


def _listen_with_knock_retries(
    ser,
    listen_s: float,
    *,
    knock: bool,
    knock_interval_s: float = 0.45,
) -> tuple[bytes, int]:
    """Listen for *listen_s*, re-knocking on an interval so boot greetings cannot
    permanently bury a one-shot identity line (#79).

    Returns (raw_bytes, knock_count). Does not clear the RX buffer — callers must
    not clear after a boot wait if they want a boot-printed identity (#81 CR).
    """
    buf = bytearray()
    knocks = 0
    t0 = time.time()
    next_knock = t0  # knock immediately
    while time.time() - t0 < listen_s:
        now = time.time()
        if knock and now >= next_knock:
            try:
                _knock_once(ser)
                knocks += 1
            except Exception:  # noqa: BLE001
                pass
            next_knock = now + knock_interval_s
        try:
            chunk = ser.read(512)
        except Exception:  # noqa: BLE001
            chunk = b""
        if chunk:
            buf.extend(chunk)
            if _identity_in_raw(bytes(buf)) is not None:
                try:
                    extra = ser.read(256)
                    if extra:
                        buf.extend(extra)
                except Exception:  # noqa: BLE001
                    pass
                break
        else:
            time.sleep(0.02)
    return bytes(buf), knocks


def _attempt_plans(reset: bool | None) -> list[tuple[str, bool]]:
    """Return (label, do_reset) attempts.

    - True: pulse only
    - False: deasserted only (default CH9102-safe)
    - None: deasserted first, then pulse fallback (#79)
    """
    if reset is True:
        return [("DTR/RTS pulse", True)]
    if reset is False:
        return [("lines held deasserted (no pulse)", False)]
    return [
        ("lines held deasserted (no pulse)", False),
        ("DTR/RTS pulse fallback", True),
    ]


def probe_serial_identity(
    port: str,
    *,
    baud: int = 115200,
    listen_s: float = 3.0,
    boot_wait_s: float = 1.5,
    reset: bool | None = False,
    knock: bool = True,
    knock_interval_s: float = 0.45,
    expect_name: str | None = None,
    expect_version: str | None = None,
) -> SerialIdentityResult:
    """Open *port*, knock ``identity``, parse response.

    Default ``reset=False``: DTR/RTS **deasserted**, no pulse (tig/silico#78).
    CH9102/M5GO: a pulse often lands ROM so the app never answers.

    Within each attempt, re-knock on *knock_interval_s* for the full *listen_s*
    window so a boot greeting cannot swallow a single knock (#79).

    ``reset=True``: clear stale RX **before** the pulse only, wait for boot, then
    listen **without** clearing again so a boot-printed ``fw_name=`` line is kept
    (#81 CR). Never ``reset_input_buffer`` after the boot wait.

    ``reset=None``: try deasserted first, then pulse fallback.

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
        msg = str(e).lower()
        lines = [f"FAIL: open {port}: {e}"]
        if any(
            x in msg
            for x in (
                "access is denied",
                "permission denied",
                "busy",
                "resource busy",
                "in use",
                "could not open port",
                "errno 16",
                "errno 13",
            )
        ):
            lines.append(
                "HINT: port may be held by another process (silico monitor, serial "
                "console, IDE). Stop the other reader, then re-run inspect/verify "
                "(tig/silico#84)."
            )
        return SerialIdentityResult(False, lines)

    raw_all = bytearray()
    last_raw = b""
    try:
        plans = _attempt_plans(reset)
        for label, do_reset in plans:
            lines.append(f"Attempt: {label}")
            _hold_deasserted(ser)
            if do_reset:
                # Drop pre-pulse noise only. Never clear after boot wait — boot-only
                # C plates print identity once and that line must survive (#81 CR).
                _clear_input(ser)
                lines.append("Pulse DTR/RTS (best-effort reset)...")
                _pulse_reset(ser)
                _hold_deasserted(ser)
                if boot_wait_s > 0:
                    lines.append(f"Wait {boot_wait_s:g}s for app boot after pulse...")
                    time.sleep(boot_wait_s)
                # Intentionally no reset_input_buffer here (preserve boot identity).
            else:
                # Stale RX only — no pulse, so no boot line to preserve from this open.
                _clear_input(ser)
            if knock:
                lines.append(
                    f"Knock: CR/LF + identity (retry every {knock_interval_s:g}s "
                    f"for {listen_s:g}s)"
                )
            raw, n_knocks = _listen_with_knock_retries(
                ser,
                listen_s,
                knock=knock,
                knock_interval_s=knock_interval_s,
            )
            last_raw = raw
            raw_all.extend(raw)
            if knock:
                lines.append(f"  knocks this attempt: {n_knocks}")
            lines.append(f"Captured {len(raw)} bytes @ {baud}")
            if raw:
                preview = raw[:160]
                lines.append(f"  raw: {preview!r}{'...' if len(raw) > 160 else ''}")

            got = _identity_in_raw(raw)
            if got is None:
                lines.append("No identity line on this attempt.")
                continue

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
                return SerialIdentityResult(False, lines, identity=got, raw=bytes(raw_all))
            if expect_name or expect_version:
                lines.append("OK: identity matches expected")
            else:
                lines.append("OK: identity present")
            return SerialIdentityResult(True, lines, identity=got, raw=bytes(raw_all))
    finally:
        try:
            ser.close()
        except Exception:  # noqa: BLE001
            pass

    lines.append("RESULT: no identity line found on serial")
    lines.append(
        "C images must answer identity on the link (not boot-print only) — "
        "print fw_name=… fw_version=… when the host sends the word identity. "
        "Boot-only plates: probe with reset=True so the boot line is not discarded."
    )
    lines.append(
        "Hint: CH9102/M5GO — default is no DTR/RTS pulse; "
        "manual: open COM with dtr=rts=False, write identity + newline."
    )
    return SerialIdentityResult(False, lines, identity=None, raw=last_raw or bytes(raw_all))
