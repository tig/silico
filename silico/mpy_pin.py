"""mpy-cross pin helpers: match device MicroPython ABI (host only)."""

from __future__ import annotations

import re
from pathlib import Path

# Plate default: latest *stable* PyPI mpy-cross we ship in the template.
# Agents must re-pin to the board after inspect (see AGENTS.md).
PLATE_DEFAULT_MPY_CROSS = "1.27.0.post2"

# Device MicroPython X.Y.Z -> installable PyPI mpy-cross pin (must exist on PyPI).
# Prefer matching-minor .postN / rc when bare X.Y.Z is unpublished.
# Keep short; extend when agents hit new gaps (file issue + PR).
KNOWN_DEVICE_TO_PIN: dict[str, str] = {
    "1.28.0": "1.28.0rc0.post2",
    "1.27.0": "1.27.0.post2",
    "1.26.1": "1.26.1.post2",
    "1.26.0": "1.26.0.post2",
    "1.25.0": "1.25.0.post2",
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
            "INFO: no device MicroPython version yet. After inspect, run "
            f"`silico inspect --port COMx --apply-mpy-pin` "
            f"(plate default is {PLATE_DEFAULT_MPY_CROSS}; Silico owns the pin)."
        )
        return lines

    dev = parse_micropython_version(device_version) or device_version
    suggest = suggest_mpy_cross_pin(dev)
    lines.append(f"Device MicroPython: {dev}")
    lines.append(f"Suggested mpy-cross pin: {suggest}")

    if dev in KNOWN_DEVICE_TO_PIN and KNOWN_DEVICE_TO_PIN[dev] != dev:
        lines.append(
            f"NOTE: stable mpy-cross=={dev} may be missing on PyPI; "
            f"Silico maps to matching-minor pin {suggest} (same .mpy ABI line). "
            "Do not leave a stale plate default."
        )

    if toml_pin:
        if same_minor(toml_pin, dev):
            lines.append(f"OK: silico.toml mpy_cross={toml_pin} matches device minor {dev}")
        else:
            lines.append(
                f"WARN: silico.toml mpy_cross={toml_pin} does not match device "
                f"MicroPython {dev} (major.minor). Run: "
                f"silico inspect --port COMx --apply-mpy-pin  (writes {suggest})."
            )
    else:
        lines.append(
            f"INFO: no mpy_cross in silico.toml; run "
            f"silico inspect --port COMx --apply-mpy-pin  (writes {suggest})."
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


def apply_mpy_cross_pin(
    device_version: str,
    *,
    root: Path | None = None,
) -> list[str]:
    """Write suggested mpy-cross pin into silico.toml and requirements-dev.txt.

    Silico owns the ABI chain: product repos should not hand-comment how to
    derive the pin. Returns human-readable action lines.
    """
    root = (root or Path.cwd()).resolve()
    dev = parse_micropython_version(device_version) or device_version.strip()
    pin = suggest_mpy_cross_pin(dev)
    lines: list[str] = [
        f"Device MicroPython: {dev}",
        f"Applying mpy-cross pin: {pin}",
    ]
    if dev in KNOWN_DEVICE_TO_PIN and KNOWN_DEVICE_TO_PIN[dev] != dev:
        lines.append(
            f"NOTE: stable mpy-cross=={dev} may be missing on PyPI; "
            f"wrote matching-minor pin {pin}."
        )

    toml_path = root / "silico.toml"
    if toml_path.is_file():
        text = toml_path.read_text(encoding="utf-8")
        if re.search(r'(?m)^\s*mpy_cross\s*=', text):
            new_text, n = re.subn(
                r'(?m)^(\s*mpy_cross\s*=\s*)["\'][^"\']*["\']',
                rf'\1"{pin}"',
                text,
                count=1,
            )
            if n:
                toml_path.write_text(new_text, encoding="utf-8")
                lines.append(f"wrote {toml_path.name} [runtime].mpy_cross = \"{pin}\"")
            else:
                lines.append(f"WARN: could not rewrite mpy_cross in {toml_path.name}")
        elif re.search(r"(?m)^\s*\[runtime\]\s*$", text):
            new_text = re.sub(
                r"(?m)^(\s*\[runtime\]\s*\n)",
                rf'\1mpy_cross = "{pin}"\n',
                text,
                count=1,
            )
            toml_path.write_text(new_text, encoding="utf-8")
            lines.append(f"wrote {toml_path.name} [runtime].mpy_cross = \"{pin}\" (inserted)")
        else:
            with toml_path.open("a", encoding="utf-8") as f:
                f.write(f'\n[runtime]\nmpy_cross = "{pin}"\n')
            lines.append(f"wrote {toml_path.name} [runtime] section with mpy_cross")
    else:
        toml_path.write_text(
            f'[runtime]\nmpy_cross = "{pin}"\n',
            encoding="utf-8",
        )
        lines.append(f"created {toml_path.name} with mpy_cross = \"{pin}\"")

    req = root / "requirements-dev.txt"
    req_line = f"mpy-cross=={pin}"
    if req.is_file():
        rtext = req.read_text(encoding="utf-8")
        if re.search(r"(?m)^\s*mpy-cross\s*==", rtext):
            new_r, n = re.subn(
                r"(?m)^\s*mpy-cross\s*==\s*\S+",
                req_line,
                rtext,
                count=1,
            )
            if n:
                req.write_text(new_r, encoding="utf-8")
                lines.append(f"wrote {req.name} {req_line}")
            else:
                lines.append(f"WARN: could not rewrite mpy-cross in {req.name}")
        else:
            with req.open("a", encoding="utf-8") as f:
                if rtext and not rtext.endswith("\n"):
                    f.write("\n")
                f.write(req_line + "\n")
            lines.append(f"appended {req.name} {req_line}")
    else:
        req.write_text(
            "# Host-only. Distribution is tig-silico (never: pip install silico).\n"
            f"{req_line}\n",
            encoding="utf-8",
        )
        lines.append(f"created {req.name} with {req_line}")

    lines.append(
        f"Next: python -m pip install -U \"mpy-cross=={pin}\"  "
        "(host only; then re-run host compile gate)."
    )
    return lines
