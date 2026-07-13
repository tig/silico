"""mpy-cross pin helpers: match device MicroPython ABI (host only)."""

from __future__ import annotations

import re
from pathlib import Path

# Plate default: latest *stable* PyPI mpy-cross we ship in the template.
# Agents must re-pin to the board after inspect (see AGENTS.md).
PLATE_DEFAULT_MPY_CROSS = "1.27.0.post2"

# When device is 1.28.0 and stable 1.28.0 is not on PyPI, matching-minor rc is OK.
# Keep this table short; extend when agents hit new gaps.
KNOWN_DEVICE_TO_PIN: dict[str, str] = {
    "1.28.0": "1.28.0rc0.post2",
    "1.27.0": "1.27.0.post2",
    "1.26.0": "1.26.1",  # fallback if needed; agents may adjust
}


def parse_micropython_version(text: str) -> str | None:
    """Extract X.Y.Z from sys.version / inspect output."""
    if not text:
        return None
    m = re.search(r"MicroPython\s+v?(\d+\.\d+\.\d+)", text, re.I)
    if m:
        return m.group(1)
    m = re.search(r"\bv?(\d+\.\d+\.\d+)\b", text)
    return m.group(1) if m else None


def parse_mpy_cross_pin(pin: str) -> tuple[int, int, int] | None:
    """Parse major.minor.patch from a pin like 1.28.0rc0.post2 or 1.27.0.post2."""
    if not pin:
        return None
    m = re.match(r"^\s*(\d+)\.(\d+)\.(\d+)", pin.strip())
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def same_minor(a: str, b: str) -> bool:
    pa, pb = parse_mpy_cross_pin(a), parse_mpy_cross_pin(b)
    if not pa or not pb:
        return False
    return pa[0] == pb[0] and pa[1] == pb[1]


def suggest_mpy_cross_pin(device_version: str) -> str:
    """Recommend a PyPI mpy-cross pin for a device MicroPython X.Y.Z."""
    ver = parse_micropython_version(device_version) or device_version.strip()
    if ver in KNOWN_DEVICE_TO_PIN:
        return KNOWN_DEVICE_TO_PIN[ver]
    # Prefer exact, then known table, then X.Y.0 as aspirational
    return ver


def pin_advice_lines(device_version: str | None, toml_pin: str | None) -> list[str]:
    """Plain-language guidance for agents/operators."""
    lines: list[str] = []
    if not device_version:
        lines.append(
            "INFO: no device MicroPython version yet. After inspect, set "
            f"silico.toml [runtime].mpy_cross and requirements-dev mpy-cross==… "
            f"(plate default is {PLATE_DEFAULT_MPY_CROSS}; re-pin to the board)."
        )
        return lines

    dev = parse_micropython_version(device_version) or device_version
    suggest = suggest_mpy_cross_pin(dev)
    lines.append(f"Device MicroPython: {dev}")
    lines.append(f"Suggested mpy-cross pin: {suggest}")

    if dev in KNOWN_DEVICE_TO_PIN and KNOWN_DEVICE_TO_PIN[dev] != dev:
        lines.append(
            f"NOTE: stable mpy-cross=={dev} may be missing on PyPI; "
            f"use matching-minor pin {suggest} (same .mpy ABI line as the device). "
            "Do not leave a stale plate default."
        )

    if toml_pin:
        if same_minor(toml_pin, dev):
            lines.append(f"OK: silico.toml mpy_cross={toml_pin} matches device minor {dev}")
        else:
            lines.append(
                f"WARN: silico.toml mpy_cross={toml_pin} does not match device "
                f"MicroPython {dev} (major.minor). Update toml + requirements-dev.txt "
                f"to {suggest}."
            )
    else:
        lines.append(
            f"INFO: no mpy_cross in silico.toml; set [runtime].mpy_cross = \"{suggest}\" "
            "and pin requirements-dev.txt the same way."
        )
    return lines


def read_toml_mpy_cross(root: Path | None = None) -> str | None:
    """Read [runtime].mpy_cross from silico.toml if present (stdlib, no tomli required)."""
    root = root or Path.cwd()
    path = root / "silico.toml"
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    # simple scan: mpy_cross = "..."
    m = re.search(r'(?m)^\s*mpy_cross\s*=\s*["\']([^"\']+)["\']', text)
    return m.group(1) if m else None
