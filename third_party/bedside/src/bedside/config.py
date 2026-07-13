"""Load and write bedside.toml (stdlib only)."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_NAME = "bedside.toml"


@dataclass
class BedsideConfig:
    """Project-local Bedside pin and paths."""

    pin: str = "main"
    contract_path: str = "third_party/bedside/contract"
    surface_path: str = "third_party/bedside/surface"
    eval_path: str = "third_party/bedside/eval"
    domain_notes: str = "BEDSIDE.md"
    agents_stub: bool = True
    # Extra fixture roots (product domain packs). Survive re-vendor of third_party/bedside.
    fixture_paths: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> BedsideConfig:
        raw_paths = data.get("fixture_paths", [])
        if isinstance(raw_paths, str):
            paths = [raw_paths]
        else:
            paths = [str(p) for p in raw_paths]
        return cls(
            pin=str(data.get("pin", "main")),
            contract_path=str(data.get("contract_path", "third_party/bedside/contract")),
            surface_path=str(data.get("surface_path", "third_party/bedside/surface")),
            eval_path=str(data.get("eval_path", "third_party/bedside/eval")),
            domain_notes=str(data.get("domain_notes", "BEDSIDE.md")),
            agents_stub=bool(data.get("agents_stub", True)),
            fixture_paths=paths,
        )


def config_path(root: Path) -> Path:
    return root / CONFIG_NAME


def load_config(root: Path) -> BedsideConfig | None:
    path = config_path(root)
    if not path.is_file():
        return None
    with path.open("rb") as f:
        data = tomllib.load(f)
    return BedsideConfig.from_dict(data)


def _toml_str(value: str) -> str:
    """Quote a string for TOML; normalize paths to forward slashes."""
    s = value.replace("\\", "/").replace('"', '\\"')
    return f'"{s}"'


def write_config(root: Path, cfg: BedsideConfig) -> Path:
    path = config_path(root)
    lines = [
        "# Bedside project config (see https://github.com/tig/bedside)",
        f"pin = {_toml_str(cfg.pin)}",
        f"contract_path = {_toml_str(cfg.contract_path)}",
        f"surface_path = {_toml_str(cfg.surface_path)}",
        f"eval_path = {_toml_str(cfg.eval_path)}",
        f"domain_notes = {_toml_str(cfg.domain_notes)}",
        f"agents_stub = {'true' if cfg.agents_stub else 'false'}",
    ]
    if cfg.fixture_paths:
        lines.append("fixture_paths = [")
        for p in cfg.fixture_paths:
            lines.append(f"  {_toml_str(p)},")
        lines.append("]")
    else:
        lines.append(
            "# fixture_paths = [\"third_party/bedside/eval/fixtures\", \"eval/fixtures\"]"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def repo_root_from_package() -> Path:
    """Directory that holds contract/, eval/, surface/ when developing this repo."""
    # src/bedside/config.py -> parents: bedside, src, repo
    return Path(__file__).resolve().parents[2]


def resolve_under(root: Path, rel: str) -> Path:
    p = Path(rel)
    if p.is_absolute():
        return p
    return (root / p).resolve()
