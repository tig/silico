#!/usr/bin/env python3
"""Throwaway serial identity probe — no mpremote, no ESP-IDF.

Usage (repo root)::

    py -3 experiments/c_backend/probe.py --port COM8
    py -3 experiments/c_backend/probe.py --self-test
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Allow running as a script without package install.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from identity import Identity, match_expected, parse_identity_blob  # noqa: E402


def _self_test() -> int:
    cases: list[tuple[str, str | None, str | None]] = [
        ("fw_name=XUSSC fw_version=0.0.1\r\n", "XUSSC", "0.0.1"),
        ("boot...\nfw_name=GCU fw_version=1.2.3\nok\n", "GCU", "1.2.3"),
        ("GCU\n0.0.1\n", "GCU", "0.0.1"),
        ("noise only\r\n", None, None),
        ("", None, None),
    ]
    failed = 0
    for blob, want_n, want_v in cases:
        got = parse_identity_blob(blob)
        if want_n is None:
            if got is not None and got.complete:
                print(f"FAIL self-test: expected no identity for {blob!r}, got {got}")
                failed += 1
            else:
                print(f"OK   no-identity for {blob!r}")
            continue
        if got is None or got.fw_name != want_n or got.fw_version != want_v:
            print(f"FAIL self-test: {blob!r} -> {got}, want {want_n}/{want_v}")
            failed += 1
        else:
            print(f"OK   {got.fw_name} {got.fw_version}")

    # match_expected
    idn = Identity("XUSSC", "0.0.1")
    if match_expected(idn, expect_name="XUSSC", expect_version="0.0.1"):
        print("FAIL match_expected should pass")
        failed += 1
    else:
        print("OK   match_expected pass")
    misses = match_expected(idn, expect_name="OTHER", expect_version="0.0.1")
    if not misses:
        print("FAIL match_expected should fail on name")
        failed += 1
    else:
        print("OK   match_expected name miss")

    return 30 if failed else 0


def _pulse_reset(ser) -> None:
    """CH340-style reset edges (best-effort; board-dependent)."""
    try:
        ser.dtr = False
        ser.rts = True
        time.sleep(0.05)
        ser.dtr = True
        ser.rts = False
        time.sleep(0.05)
        ser.dtr = False
        time.sleep(0.1)
    except Exception as e:  # noqa: BLE001 — probe must stay chatty
        print(f"WARN: DTR/RTS pulse failed: {e}")


def probe(
    port: str,
    *,
    baud: int = 115200,
    reset: bool = True,
    listen_s: float = 2.0,
    knock: bool = True,
    expect_name: str | None = None,
    expect_version: str | None = None,
) -> int:
    try:
        import serial
        from serial.tools import list_ports
    except ImportError:
        print("FAIL: pyserial not installed (pip install pyserial)")
        return 30

    listed = {p.device.upper(): p for p in list_ports.comports()}
    info = listed.get(port.upper())
    print(f"Port: {port}")
    if info is None:
        print(f"FAIL: {port} not in serial inventory. Plug cable; re-run.")
        return 30
    vid = f"{info.vid:04X}" if info.vid is not None else "?"
    pid = f"{info.pid:04X}" if info.pid is not None else "?"
    print(f"  desc: {info.description}")
    print(f"  vid:pid: {vid}:{pid}")
    print(f"  hwid: {info.hwid}")
    print("  note: high-level chip ID is not available over CH340 without firmware.")
    print("  mode: serial identity knock (no mpremote, no esptool)")

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
        print(f"FAIL: open {port}: {e}")
        return 30

    try:
        if reset:
            print("Pulse DTR/RTS (best-effort reset)...")
            _pulse_reset(ser)
        ser.reset_input_buffer()

        if knock:
            print("Knock: CR/LF + identity")
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

    print(f"Captured {len(raw)} bytes @ {baud}")
    if raw:
        print(f"  raw: {raw[:120]!r}{'…' if len(raw) > 120 else ''}")
        try:
            text_preview = raw.decode("utf-8", errors="replace")
            print(f"  text preview:\n{text_preview[:400]}")
        except Exception:
            pass
    else:
        print("  (empty capture)")

    text = raw.decode("utf-8", errors="replace")
    got = parse_identity_blob(text)
    if got is None or not (got.fw_name or got.fw_version):
        print("RESULT: no identity line found")
        print(
            "This is expected on a silent Artemis ATP (Apollo3) with stock/binary "
            "firmware. ESP-IDF flash will not work on this MCU."
        )
        print(
            "Next metal proof for #53: use an ESP32-class port (e.g. COM7 CH9102) "
            "or flash a tiny C image that prints: fw_name=… fw_version=…"
        )
        return 10

    print(f"RESULT: identity fw_name={got.fw_name!r} fw_version={got.fw_version!r}")
    if got.raw_line:
        print(f"  from: {got.raw_line!r}")
    fails = match_expected(got, expect_name=expect_name, expect_version=expect_version)
    if fails:
        for line in fails:
            print(line)
        return 10
    if expect_name or expect_version:
        print("OK: identity matches expected")
    else:
        print("OK: identity present (no --expect-* given)")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Throwaway serial identity probe (#53)")
    p.add_argument("--port", help="COMx / /dev/tty… (required unless --self-test)")
    p.add_argument("--baud", type=int, default=115200)
    p.add_argument("--listen", type=float, default=2.0, help="seconds to read after knock")
    p.add_argument("--no-reset", action="store_true", help="skip DTR/RTS pulse")
    p.add_argument("--no-knock", action="store_true", help="listen only, no identity command")
    p.add_argument("--expect-name", default=None)
    p.add_argument("--expect-version", default=None)
    p.add_argument("--self-test", action="store_true", help="parser tests only")
    args = p.parse_args(argv)

    if args.self_test:
        return _self_test()
    if not args.port:
        print("FAIL: --port is required (or pass --self-test)")
        return 30
    return probe(
        args.port,
        baud=args.baud,
        reset=not args.no_reset,
        listen_s=args.listen,
        knock=not args.no_knock,
        expect_name=args.expect_name,
        expect_version=args.expect_version,
    )


if __name__ == "__main__":
    raise SystemExit(main())
