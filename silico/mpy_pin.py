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
    """Extract MicroPython X.Y.Z from inspect / sys output.

    Prefer explicit MicroPython banners and ``sys.implementation`` tuples.
    Never treat a bare language version (e.g. ``3.4.0`` on ancient ports) as
    the MicroPython release — that led to nonsense mpy-cross pins.
    """
    if not text:
        return None
    m = re.search(r"MicroPython\s+v?(\d+\.\d+\.\d+)", text, re.I)
    if m:
        return m.group(1)
    # sys.implementation repr: (name='micropython', version=(1, 28, 0), ...)
    m = re.search(
        r"name\s*=\s*['\"]micropython['\"][^\n]*version\s*=\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)",
        text,
        re.I,
    )
    if m:
        return f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
    m = re.search(r"version\s*=\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", text)
    if m:
        maj = int(m.group(1))
        # Language versions are 3.x; MicroPython releases are 1.x today.
        if maj == 1:
            return f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
    # Last resort: first X.Y.Z that is not a 3.x language version
    for m in re.finditer(r"\bv?(\d+)\.(\d+)\.(\d+)\b", text):
        maj, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if maj == 3 and minor <= 14:
            continue
        return f"{maj}.{minor}.{patch}"
    return None


def is_ancient_micropython(device_version: str | None, *, minor_floor: int = 20) -> bool:
    """True if device MicroPython is older than 1.<minor_floor> (upgrade before pin)."""
    if not device_version:
        return False
    ver = parse_micropython_version(device_version) or device_version.strip()
    parsed = parse_mpy_cross_pin(ver)
    if not parsed:
        return False
    maj, minor, _patch = parsed
    return maj == 1 and minor < minor_floor


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

    if is_ancient_micropython(dev):
        lines.append(
            "WARN: device MicroPython looks ancient (< 1.20). "
            "Prefer a first-flash of a current port build (UF2 or esptool) before "
            "`--apply-mpy-pin` — old UIFlow-era images mislead ABI pins."
        )

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


# A TOML table header: [runtime], [tool.foo], or [[array.of.tables]].
_TABLE_HEADER = re.compile(r"(?m)^[ \t]*\[\[?[^\]\n]+\]\]?[ \t]*(?:#.*)?$")
_MPY_CROSS_KEY = re.compile(r'(?m)^([ \t]*mpy_cross[ \t]*=[ \t]*)(["\'])([^"\']*)\2')


def _runtime_body_span(text: str) -> tuple[int, int] | None:
    """Char span of the [runtime] table's body, or None if the table is absent.

    Keys must be resolved inside their own table: a bare search for `mpy_cross`
    will happily match (and rewrite) a key belonging to some other table.
    """
    header = re.search(r"(?m)^[ \t]*\[runtime\][ \t]*(?:#.*)?$", text)
    if not header:
        return None
    start = header.end()
    nxt = _TABLE_HEADER.search(text, start)
    return start, (nxt.start() if nxt else len(text))


def read_toml_mpy_cross(root: Path | None = None) -> str | None:
    """Read [runtime].mpy_cross from silico.toml if present (stdlib, no tomli required)."""
    root = root or Path.cwd()
    path = root / "silico.toml"
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    span = _runtime_body_span(text)
    if span is None:
        return None
    m = _MPY_CROSS_KEY.search(text, *span)
    return m.group(3) if m else None


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
        span = _runtime_body_span(text)
        if span is None:
            # No [runtime] table at all — append one.
            sep = "" if text.endswith("\n") or not text else "\n"
            toml_path.write_text(
                f'{text}{sep}\n[runtime]\nmpy_cross = "{pin}"\n', encoding="utf-8"
            )
            lines.append(f"wrote {toml_path.name} [runtime] section with mpy_cross")
        else:
            existing = _MPY_CROSS_KEY.search(text, *span)
            if existing:
                new_text = (
                    text[: existing.start()]
                    + f'{existing.group(1)}"{pin}"'
                    + text[existing.end() :]
                )
                toml_path.write_text(new_text, encoding="utf-8")
                lines.append(f'wrote {toml_path.name} [runtime].mpy_cross = "{pin}"')
            else:
                # [runtime] exists but has no pin — insert at the top of its body.
                body_start = span[0]
                new_text = (
                    text[:body_start] + f'\nmpy_cross = "{pin}"' + text[body_start:]
                )
                toml_path.write_text(new_text, encoding="utf-8")
                lines.append(
                    f'wrote {toml_path.name} [runtime].mpy_cross = "{pin}" (inserted)'
                )
    else:
        toml_path.write_text(
            f'[runtime]\nmpy_cross = "{pin}"\n',
            encoding="utf-8",
        )
        lines.append(f'created {toml_path.name} with mpy_cross = "{pin}"')

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
