"""Run esptool with operator-visible progress (streamed stdout/stderr).

First-flash of MicroPython on ESP32-class boards uses the ROM bootloader path.
esptool already prints percentages; we must not capture output into a black hole.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

ProgressCallback = Callable[[str], None]


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


def run_esptool_streaming(
    args: list[str],
    *,
    on_progress: ProgressCallback | None = None,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run esptool, streaming progress lines to the operator.

    esptool often updates a single line with ``\\r`` (progress bar). We split on
    both ``\\n`` and ``\\r`` so each percentage update becomes a progress line
    agents can show. When stdout is a TTY and no callback is set, inherit the
    terminal so native bars still work.
    """
    cmd = [*esptool_cmd_prefix(), *args]
    inherit = on_progress is None and sys.stdout.isatty()
    if inherit:
        r = subprocess.run(cmd, check=False, timeout=timeout)
        return subprocess.CompletedProcess(cmd, r.returncode, "", "")

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert proc.stdout is not None
    chunks: list[str] = []
    buf = ""
    try:
        while True:
            ch = proc.stdout.read(1)
            if ch == "" and proc.poll() is not None:
                break
            if ch == "":
                continue
            if ch in ("\n", "\r"):
                line = buf.strip()
                buf = ""
                if line:
                    chunks.append(line)
                    if on_progress is not None:
                        on_progress(f"PROGRESS [esptool] {line}")
                continue
            buf += ch
            # Flush long lines without CR (some esptool builds)
            if len(buf) > 200 and "Writing" in buf:
                line = buf.strip()
                buf = ""
                chunks.append(line)
                if on_progress is not None:
                    on_progress(f"PROGRESS [esptool] {line}")
        if buf.strip():
            line = buf.strip()
            chunks.append(line)
            if on_progress is not None:
                on_progress(f"PROGRESS [esptool] {line}")
        proc.wait(timeout=timeout)
    except Exception:
        proc.kill()
        raise
    out = "\n".join(chunks)
    return subprocess.CompletedProcess(cmd, proc.returncode or 0, out, "")


def copy_with_progress(
    src: Path,
    dest: Path,
    *,
    on_progress: ProgressCallback | None = None,
    chunk_size: int = 256 * 1024,
) -> None:
    """Copy a UF2 (or other image) with byte progress for the operator."""
    total = src.stat().st_size
    written = 0
    last_pct = -1
    dest.parent.mkdir(parents=True, exist_ok=True)
    with src.open("rb") as inf, dest.open("wb") as outf:
        while True:
            block = inf.read(chunk_size)
            if not block:
                break
            outf.write(block)
            written += len(block)
            pct = int(100 * written / total) if total else 100
            if on_progress is not None and (pct != last_pct or written == total):
                # Throttle: every 5% or completion
                if pct == 100 or pct // 5 != last_pct // 5:
                    on_progress(
                        f"PROGRESS [uf2-copy] {pct}% "
                        f"({_fmt(written)} / {_fmt(total)}) -> {dest}"
                    )
                    last_pct = pct


def _fmt(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KiB"
    return f"{n / (1024 * 1024):.2f} MiB"
