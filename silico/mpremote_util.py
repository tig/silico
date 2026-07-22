"""Thin wrappers around mpremote (optional host tool)."""

from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path


def mpremote_available() -> bool:
    return shutil.which("mpremote") is not None or _module_ok()


def _module_ok() -> bool:
    try:
        import mpremote  # noqa: F401

        return True
    except ImportError:
        return False


RAW_REPL_ERR = "could not enter raw repl"

# Shared recovery text (inspect/deploy append; keep short — agents load stderr).
# #49: knock protocol door. #62: do not thrash; TX alone ≠ duplex; stock MP park.
LOCKOUT_RECOVERY = (
    "silico: app owns the console (Ctrl-C is data); knocked `repl` — door stayed shut "
    "(tig/silico#49 #62).\n"
    "Do NOT thrash redeploy. Files may already be on the device. Host green ≠ duplex.\n"
    "TX/telem alone is not metal OK. Recover **once**, park stock MicroPython, stop:\n"
    "  ESP32: esptool --chip esp32 --port COMx erase-flash && "
    "esptool --chip esp32 --port COMx write-flash -z 0x1000 ESP32_GENERIC-<ver>.bin\n"
    "  RP2040: BOOT+RESET → RPI-RP2 → MicroPython .uf2\n"
    "Then: silico inspect --port COMx  (REPL; stock boot.py only).\n"
    "Serial ladder + ESP32 UART footguns: silico/knowledge/esp32-usb-serial.md"
)

# Back-compat name used in older tests/docs.
_DOOR_HINT = LOCKOUT_RECOVERY


def knock_protocol_door(port: str, wait_s: float = 2.5) -> bool:
    """Ask a console-hardened GCU app to step aside (its `repl` verb).

    GCU specs that treat Ctrl-C as data make raw-REPL entry impossible while
    the app runs; well-behaved apps ship a `repl` protocol command that coasts
    actuators and exits to the interpreter. Returns True if the knock was
    delivered (not whether the door opened — the retry decides that).
    """
    try:
        import serial  # pyserial, via mpremote's own dependency
    except ImportError:
        return False
    try:
        with serial.Serial(port, 115200, timeout=1) as sp:
            sp.write(b"repl\r\n")
            sp.flush()
    except Exception:
        return False
    time.sleep(wait_s)
    return True


def run_mpremote(
    port: str, *args: str, timeout: float = 30.0, knock: bool = True
) -> subprocess.CompletedProcess[str]:
    cmd = ["mpremote", "connect", port, *args]
    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if knock and r.returncode != 0 and RAW_REPL_ERR in (r.stderr or "").lower():
        if knock_protocol_door(port):
            r2 = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, check=False
            )
            if r2.returncode == 0:
                return r2
            r = r2
        r.stderr = (r.stderr or "") + "\n" + LOCKOUT_RECOVERY + "\n"
    return r


def exec_on_device(port: str, code: str, timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
    return run_mpremote(port, "exec", code, timeout=timeout)


def ls_device(port: str) -> subprocess.CompletedProcess[str]:
    return run_mpremote(port, "ls", ":")


def cp_to_device(port: str, local: Path, remote_name: str) -> subprocess.CompletedProcess[str]:
    return run_mpremote(port, "cp", str(local), f":{remote_name}")
