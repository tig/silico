"""Run esptool / UF2 copy with operator-visible progress via ProgressLog."""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

from silico.progress import ProgressLog, format_bytes


def esptool_available() -> bool:
    if shutil.which("esptool") or shutil.which("esptool.py"):
        return True
    try:
        import esptool  # noqa: F401

        return True
    except ImportError:
        return False


def esptool_cmd_prefix() -> list[str]:
    """Prefer console script; fall back to python -m esptool."""
    for name in ("esptool", "esptool.py"):
        path = shutil.which(name)
        if path:
            return [path]
    return [sys.executable, "-m", "esptool"]


def _emit_stream_chunks(buf: str, log: ProgressLog, prefix: str) -> str:
    """Split on CR/LF; emit complete lines; return residual buffer."""
    while True:
        i_n = buf.find("\n")
        i_r = buf.find("\r")
        if i_n < 0 and i_r < 0:
            return buf
        if i_n < 0:
            cut = i_r
        elif i_r < 0:
            cut = i_n
        else:
            cut = min(i_n, i_r)
        line = buf[:cut].strip()
        buf = buf[cut + 1 :]
        if line:
            log(f"{prefix}{line}")
    return buf


def run_esptool_streaming(
    args: list[str],
    *,
    log: ProgressLog,
    timeout: float | None = 600.0,
) -> int:
    """Run esptool; stream progress into ``log`` (full transcript).

    Splits on ``\\r`` and ``\\n`` so percentage updates become PROGRESS lines.
    Returns process exit code.
    """
    cmd = [*esptool_cmd_prefix(), *args]
    log(f"PROGRESS [esptool] $ {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert proc.stdout is not None
    buf = ""
    deadline = time.monotonic() + timeout if timeout else None
    try:
        while True:
            if deadline is not None and time.monotonic() > deadline:
                proc.kill()
                log("FAIL: esptool timed out")
                proc.wait(timeout=5)
                return 124
            chunk = proc.stdout.read(256)
            if chunk:
                buf = _emit_stream_chunks(buf + chunk, log, "PROGRESS [esptool] ")
                continue
            if proc.poll() is not None:
                break
            time.sleep(0.05)
        if buf.strip():
            log(f"PROGRESS [esptool] {buf.strip()}")
        return int(proc.wait(timeout=5) or 0)
    except Exception:
        proc.kill()
        raise


def copy_with_progress(
    src: Path,
    dest: Path,
    *,
    log: ProgressLog,
    chunk_size: int = 256 * 1024,
) -> None:
    """Copy a UF2 (or other image); percent lines go into ``log``."""
    total = src.stat().st_size
    written = 0
    last_bucket = -1
    dest.parent.mkdir(parents=True, exist_ok=True)
    with src.open("rb") as inf, dest.open("wb") as outf:
        while True:
            block = inf.read(chunk_size)
            if not block:
                break
            outf.write(block)
            written += len(block)
            pct = int(100 * written / total) if total else 100
            bucket = pct // 5
            if pct == 100 or bucket != last_bucket:
                log(
                    f"PROGRESS [uf2-copy] {pct}% "
                    f"({format_bytes(written)} / {format_bytes(total)}) -> {dest}"
                )
                last_bucket = bucket
