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


def read_product_defaults_path(root: Path | None = None) -> str | None:
    """Optional path to shipped defaults module from [host].product_defaults.

    Example::

        [host]
        product_defaults = "firmware/defaults.py"
    """
    data = _load(root)
    host = data.get("host")
    if not isinstance(host, dict):
        return None
    raw = host.get("product_defaults")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return None


def read_host_gate(root: Path | None = None) -> str | None:
    """Optional host gate command from [host].gate (C GCUs use cmake/ctest)."""
    data = _load(root)
    host = data.get("host")
    if not isinstance(host, dict):
        return None
    raw = host.get("gate")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return None


def _runtime_section(root: Path | None = None) -> dict:
    data = _load(root)
    runtime = data.get("runtime")
    return runtime if isinstance(runtime, dict) else {}


def read_runtime_language(root: Path | None = None) -> str:
    """Return ``micropython`` (default) or ``c`` from [runtime].language."""
    raw = _runtime_section(root).get("language")
    if isinstance(raw, str) and raw.strip():
        return raw.strip().lower()
    return "micropython"


def read_runtime_toolchain(root: Path | None = None) -> str | None:
    raw = _runtime_section(root).get("toolchain")
    if isinstance(raw, str) and raw.strip():
        return raw.strip().lower()
    return None


def read_esp_idf_pin(root: Path | None = None) -> str | None:
    raw = _runtime_section(root).get("esp_idf")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return None


def read_runtime_chip(root: Path | None = None) -> str | None:
    raw = _runtime_section(root).get("chip")
    if isinstance(raw, str) and raw.strip():
        return raw.strip().lower()
    return None


def read_runtime_board(root: Path | None = None) -> str | None:
    raw = _runtime_section(root).get("board")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return None


def read_deploy_mode(root: Path | None = None) -> str | None:
    """Optional [deploy].mode: ``idf-flash`` for C, file-copy default for mpy."""
    data = _load(root)
    deploy = data.get("deploy")
    if not isinstance(deploy, dict):
        return None
    raw = deploy.get("mode")
    if isinstance(raw, str) and raw.strip():
        return raw.strip().lower()
    return None


def read_deploy_project(root: Path | None = None) -> str | None:
    """IDF project directory relative to root ([deploy].project)."""
    data = _load(root)
    deploy = data.get("deploy")
    if not isinstance(deploy, dict):
        return None
    raw = deploy.get("project")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return None


def read_serial_baud(root: Path | None = None) -> int:
    """Serial baud for C identity inspect ([runtime].baud, default 115200)."""
    raw = _runtime_section(root).get("baud")
    if isinstance(raw, int) and raw > 0:
        return raw
    if isinstance(raw, str) and raw.strip().isdigit():
        return int(raw.strip())
    return 115200


def read_hal_allow_device_headers(root: Path | None = None) -> list[str]:
    """Stems allowed to #include freertos / esp_* / driver (C HAL backends).

    Example::

        [hal]
        allow_device_headers = ["hal_board", "board_m5go"]
    """
    data = _load(root)
    hal = data.get("hal")
    if not isinstance(hal, dict):
        return []
    raw = hal.get("allow_device_headers")
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        if isinstance(item, str) and item.strip():
            stem = Path(item.strip()).stem
            if stem:
                out.append(stem)
    return out
