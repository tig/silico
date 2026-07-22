"""Language-agnostic firmware identity lines (inspect / deploy verify).

Expected product shape (one line, space-separated key=value tokens)::

    fw_name=XUSSC fw_version=0.0.1

Also accepts MicroPython-style two-line dumps::

    XUSSC
    0.0.1
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_KV = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)")
_VER = re.compile(r"^\d+\.\d+(\.\d+)?([a-zA-Z0-9._+-]*)?$")


@dataclass(frozen=True)
class Identity:
    fw_name: str | None
    fw_version: str | None
    raw_line: str | None = None

    @property
    def complete(self) -> bool:
        return bool(self.fw_name and self.fw_version)


def parse_identity_blob(text: str) -> Identity | None:
    """Find the best identity in a serial capture or process output blob."""
    if not text:
        return None

    best: Identity | None = None
    for line in text.splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        kv = {m.group(1).lower(): m.group(2) for m in _KV.finditer(line)}
        name = kv.get("fw_name") or kv.get("name")
        ver = kv.get("fw_version") or kv.get("version")
        if name or ver:
            cand = Identity(name, ver, raw_line=line)
            if cand.complete:
                return cand
            if best is None or (cand.fw_name and not best.fw_name):
                best = cand
    if best is not None:
        return best

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for i in range(len(lines) - 1):
        a, b = lines[i], lines[i + 1]
        if "=" in a or "=" in b:
            continue
        if _VER.match(b) and re.match(r"^[A-Za-z][A-Za-z0-9_.-]{0,31}$", a):
            return Identity(a, b, raw_line=f"{a}\n{b}")
    return None


def match_expected(
    got: Identity,
    *,
    expect_name: str | None,
    expect_version: str | None,
) -> list[str]:
    """Return failure lines; empty means OK (or nothing expected)."""
    fails: list[str] = []
    if expect_name is not None and got.fw_name != expect_name:
        fails.append(f"FAIL: fw_name want {expect_name!r} got {got.fw_name!r}")
    if expect_version is not None and got.fw_version != expect_version:
        fails.append(f"FAIL: fw_version want {expect_version!r} got {got.fw_version!r}")
    return fails
