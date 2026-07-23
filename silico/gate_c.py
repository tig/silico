"""C/ESP-IDF host gate: include hygiene + optional [host].gate command."""

from __future__ import annotations

import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from silico.config_toml import read_hal_allow_device_headers, read_host_gate
from silico.runtime import resolve_runtime

# Device-only include prefixes / names (hygiene denylist for non-allowlisted TUs).
_DEVICE_INCLUDE = re.compile(
    r'^\s*#\s*include\s*[<"]('
    r"freertos/|"
    r"driver/|"
    r"esp_|"
    r"hal/|"
    r"soc/|"
    r"esp32|"
    r"sdkconfig|"
    r"nvs_flash|"
    r"esp_system|"
    r"esp_timer|"
    r"esp_rom|"
    r"esp_wifi|"
    r"esp_event|"
    r"esp_netif|"
    r"esp_http|"
    r"esp_https|"
    r"esp_adc|"
    r"esp_lcd|"
    r"bootloader_|"
    r"xtensa/|"
    r"riscv/"
    r")",
    re.MULTILINE | re.IGNORECASE,
)

_SOURCE_GLOBS = ("**/*.c", "**/*.h", "**/*.cpp", "**/*.hpp", "**/*.cc")
_SKIP_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "build",
        "cmake-build-debug",
        "cmake-build-release",
        "__pycache__",
        "managed_components",
        "third_party",
    }
)


@dataclass
class CGateReport:
    ok: bool
    lines: list[str] = field(default_factory=list)


def _iter_source_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for pattern in _SOURCE_GLOBS:
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            if any(part in _SKIP_DIRS for part in path.relative_to(root).parts):
                continue
            out.append(path)
    return sorted(set(out))


def _is_allowlisted(path: Path, root: Path, allow: set[str]) -> bool:
    """Allowlist by file stem only (e.g. hal_board.c → hal_board)."""
    del root  # reserved for future exact-path allowlists
    return path.stem in allow


def scan_device_includes(
    root: Path,
    *,
    allow: set[str] | None = None,
) -> list[str]:
    """Return FAIL lines for non-allowlisted TUs that pull device headers."""
    allow = allow if allow is not None else set(read_hal_allow_device_headers(root))
    fails: list[str] = []
    for path in _iter_source_files(root):
        if _is_allowlisted(path, root, allow):
            continue
        # firmware/ board tree: only allowlisted stems may use device headers;
        # portable src/ and include/ never may.
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in _DEVICE_INCLUDE.finditer(text):
            # line number
            lineno = text.count("\n", 0, m.start()) + 1
            rel = path.relative_to(root).as_posix()
            fails.append(
                f"FAIL: {rel}:{lineno} includes device header {m.group(1)!r} — "
                f"only [hal].allow_device_headers stems may (stem={path.stem!r})."
            )
    return fails


def run_host_gate_command(
    root: Path,
    command: str | None = None,
    *,
    timeout_s: float = 300.0,
) -> tuple[bool, list[str]]:
    """Run [host].gate shell command in *root*. Returns (ok, lines)."""
    cmd = command if command is not None else read_host_gate(root)
    lines: list[str] = []
    if not cmd:
        lines.append(
            "WARN: no [host].gate command — skip subprocess host build/test "
            "(set gate = \"cmake --build build/host --target host_test\")."
        )
        return True, lines

    lines.append(f"Running host gate: {cmd}")
    try:
        # Prefer argv split; shell=True only on Windows when needed for .bat/cmake paths.
        if sys.platform == "win32":
            completed = subprocess.run(
                cmd,
                shell=True,
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
            )
        else:
            completed = subprocess.run(
                shlex.split(cmd),
                shell=False,
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
            )
    except subprocess.TimeoutExpired:
        lines.append(f"FAIL: host gate timed out after {timeout_s}s: {cmd}")
        return False, lines
    except OSError as e:
        lines.append(f"FAIL: host gate could not start: {e}")
        return False, lines

    if completed.stdout:
        for line in completed.stdout.strip().splitlines()[:40]:
            lines.append(f"  | {line}")
    if completed.stderr:
        for line in completed.stderr.strip().splitlines()[:20]:
            lines.append(f"  ! {line}")
    if completed.returncode != 0:
        lines.append(f"FAIL: host gate exit {completed.returncode}")
        return False, lines
    lines.append("OK: host gate command succeeded")
    return True, lines


def run_c_gate(root: Path | None = None, *, run_command: bool = True) -> CGateReport:
    """Include hygiene (+ optional host gate command) for language=c GCUs."""
    root = (root or Path.cwd()).resolve()
    lines: list[str] = [f"C host gate root: {root}"]
    ok = True

    cfg = resolve_runtime(root)
    if cfg.language != "c":
        lines.append(
            f"INFO: runtime language={cfg.language} — use silico gate MicroPython path."
        )
        return CGateReport(True, lines)

    allow = set(read_hal_allow_device_headers(root))
    if allow:
        lines.append("device-header allowlist: " + ", ".join(sorted(allow)))
    else:
        lines.append(
            "device-header allowlist: (empty — no .c/.h may include freertos/esp_*/driver)"
        )

    fails = scan_device_includes(root, allow=allow)
    if fails:
        ok = False
        lines.extend(fails)
    else:
        lines.append("OK: no illegal device headers outside allowlist")

    if run_command:
        cmd_ok, cmd_lines = run_host_gate_command(root, cfg.host_gate)
        lines.extend(cmd_lines)
        if not cmd_ok:
            ok = False

    if ok:
        lines.append("OK: C host gate passed.")
    else:
        lines.append("FAIL: C host gate — fix before claiming host-first for language=c.")
    return CGateReport(ok=ok, lines=lines)
