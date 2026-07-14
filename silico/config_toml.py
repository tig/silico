"""Minimal silico.toml reader (stdlib only)."""

from __future__ import annotations

import tomllib
from pathlib import Path


def _load(root: Path | None = None) -> dict:
    root = root or Path.cwd()
    path = root / "silico.toml"
    if not path.is_file():
        return {}
    with path.open("rb") as f:
        try:
            data = tomllib.load(f)
        except tomllib.TOMLDecodeError:
            return {}
    return data if isinstance(data, dict) else {}


def read_toml_text(root: Path | None = None) -> str | None:
    root = root or Path.cwd()
    path = root / "silico.toml"
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def read_deploy_core(root: Path | None = None) -> list[str]:
    """Return ordered local paths from [deploy] core = [\"…\", …]."""
    data = _load(root)
    deploy = data.get("deploy")
    if not isinstance(deploy, dict):
        return []
    core = deploy.get("core")
    if not isinstance(core, list):
        return []
    out: list[str] = []
    for item in core:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def read_product_identity(root: Path | None = None) -> tuple[str | None, str | None]:
    data = _load(root)
    product = data.get("product")
    if not isinstance(product, dict):
        # also allow top-level fw_name / fw_version (plate style)
        name = data.get("fw_name")
        ver = data.get("fw_version")
        if not isinstance(name, str):
            name = None
        if not isinstance(ver, str):
            ver = None
        if name or ver:
            return name, ver
        return None, None
    name = product.get("fw_name") or product.get("name")
    ver = product.get("fw_version") or product.get("version")
    return (
        name if isinstance(name, str) else None,
        ver if isinstance(ver, str) else None,
    )


def read_hal_allow_machine(root: Path | None = None) -> list[str]:
    """Module stems allowed to import ``machine`` (device HAL backends only).

    Example silico.toml::

        [hal]
        allow_machine = ["hal_board"]
    """
    data = _load(root)
    hal = data.get("hal")
    if not isinstance(hal, dict):
        return []
    raw = hal.get("allow_machine")
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        if isinstance(item, str) and item.strip():
            # accept "hal_board" or "firmware/hal_board.py"
            stem = Path(item.strip()).stem
            if stem:
                out.append(stem)
    return out
