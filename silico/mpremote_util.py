"""Thin wrappers around mpremote (optional host tool)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def mpremote_available() -> bool:
    return shutil.which("mpremote") is not None or _module_ok()


def _module_ok() -> bool:
    try:
        import mpremote  # noqa: F401

        return True
    except ImportError:
        return False


def run_mpremote(port: str, *args: str, timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
    cmd = ["mpremote", "connect", port, *args]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def exec_on_device(port: str, code: str, timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
    return run_mpremote(port, "exec", code, timeout=timeout)


def ls_device(port: str) -> subprocess.CompletedProcess[str]:
    return run_mpremote(port, "ls", ":")


def cp_to_device(port: str, local: Path, remote_name: str) -> subprocess.CompletedProcess[str]:
    return run_mpremote(port, "cp", str(local), f":{remote_name}")
