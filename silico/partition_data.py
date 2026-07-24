"""Data-partition assets for language=c deploy (no free-form esptool essay).

Configure in silico.toml::

    [[deploy.data]]
    name = "song"
    file = "assets/first.u8.raw"
    partition = "storage"       # name column in partitions.csv
    # offset = "0x210000"       # optional explicit override

``silico deploy`` plans these after the app image and flashes with esptool
only after ``--yes`` (same confirm manners as the IDF image) — tig/silico#79.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from silico.config_toml import _load

_OFFSET_RE = re.compile(r"^(0x[0-9a-fA-F]+|\d+)$")


@dataclass(frozen=True)
class DataAssetSpec:
    """One configured data-partition payload."""

    name: str
    file: str  # repo-relative path as configured
    partition: str | None = None
    offset_raw: str | None = None  # explicit hex/dec if set


@dataclass(frozen=True)
class ResolvedDataAsset:
    name: str
    host_path: Path
    offset: int
    partition: str | None
    size: int


def parse_offset(raw: str | int) -> int:
    if isinstance(raw, int):
        if raw < 0:
            raise ValueError(f"negative offset: {raw}")
        return raw
    s = str(raw).strip()
    if not _OFFSET_RE.match(s):
        raise ValueError(f"bad offset {raw!r}")
    return int(s, 0)


def parse_partitions_csv(text: str) -> dict[str, int]:
    """Map partition name → offset from an ESP-IDF partitions.csv body.

    Skips comments and blank lines. Offset may be hex (0x…) or decimal.
    """
    out: dict[str, int] = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        # Name, Type, SubType, Offset, Size, Flags
        parts = [p.strip() for p in s.split(",")]
        if len(parts) < 4:
            continue
        name, _typ, _sub, off = parts[0], parts[1], parts[2], parts[3]
        if not name or name.lower() == "name":
            continue
        try:
            out[name] = parse_offset(off)
        except ValueError:
            continue
    return out


def load_partitions_csv(path: Path) -> dict[str, int]:
    try:
        return parse_partitions_csv(path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return {}


def read_deploy_data_specs(root: Path | None = None) -> list[DataAssetSpec]:
    """Read ``[[deploy.data]]`` array-of-tables from silico.toml."""
    data = _load(root)
    deploy = data.get("deploy")
    if not isinstance(deploy, dict):
        return []
    raw = deploy.get("data")
    if not isinstance(raw, list):
        return []
    out: list[DataAssetSpec] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        file_ = item.get("file")
        if not isinstance(name, str) or not name.strip():
            continue
        if not isinstance(file_, str) or not file_.strip():
            continue
        part = item.get("partition")
        off = item.get("offset")
        out.append(
            DataAssetSpec(
                name=name.strip(),
                file=file_.strip(),
                partition=part.strip() if isinstance(part, str) and part.strip() else None,
                offset_raw=str(off).strip() if off is not None and str(off).strip() else None,
            )
        )
    return out


def resolve_data_assets(
    root: Path,
    specs: list[DataAssetSpec] | None = None,
    *,
    partitions_csv: Path | None = None,
    project: str = "firmware",
) -> tuple[list[ResolvedDataAsset], list[str]]:
    """Resolve host paths + flash offsets. Returns (assets, error lines)."""
    root = root.resolve()
    specs = specs if specs is not None else read_deploy_data_specs(root)
    if not specs:
        return [], []

    csv_path = partitions_csv
    if csv_path is None:
        for cand in (
            root / project / "partitions.csv",
            root / "partitions.csv",
            root / project / "partitions.prod.csv",
        ):
            if cand.is_file():
                csv_path = cand
                break
    table = load_partitions_csv(csv_path) if csv_path else {}

    resolved: list[ResolvedDataAsset] = []
    errors: list[str] = []
    for spec in specs:
        # Refuse path escape: resolved file must stay under the GCU root (PR #80 CR).
        try:
            host = (root / spec.file).resolve()
        except OSError as e:
            errors.append(f"FAIL: deploy.data {spec.name!r}: bad path {spec.file!r}: {e}")
            continue
        try:
            host.relative_to(root)
        except ValueError:
            errors.append(
                f"FAIL: deploy.data {spec.name!r}: file escapes repo root "
                f"({spec.file!r}) — keep assets under the GCU checkout."
            )
            continue
        if not host.is_file():
            errors.append(f"FAIL: deploy.data {spec.name!r}: file missing: {spec.file}")
            continue
        offset: int | None = None
        if spec.offset_raw:
            try:
                offset = parse_offset(spec.offset_raw)
            except ValueError as e:
                errors.append(f"FAIL: deploy.data {spec.name!r}: {e}")
                continue
        elif spec.partition:
            if spec.partition not in table:
                errors.append(
                    f"FAIL: deploy.data {spec.name!r}: partition {spec.partition!r} "
                    f"not in {csv_path or 'partitions.csv'}"
                )
                continue
            offset = table[spec.partition]
        else:
            # try name as partition name
            if spec.name in table:
                offset = table[spec.name]
            else:
                errors.append(
                    f"FAIL: deploy.data {spec.name!r}: set partition= or offset= "
                    f"(or name a partitions.csv entry)"
                )
                continue
        try:
            size = host.stat().st_size
        except OSError as e:
            errors.append(f"FAIL: deploy.data {spec.name!r}: {e}")
            continue
        resolved.append(
            ResolvedDataAsset(
                name=spec.name,
                host_path=host,
                offset=offset,
                partition=spec.partition or (spec.name if spec.name in table else None),
                size=size,
            )
        )
    return resolved, errors


def plan_data_lines(assets: list[ResolvedDataAsset], *, port: str) -> list[str]:
    if not assets:
        return []
    lines = [
        "Data partitions (flashed after app image, same --yes confirm):",
    ]
    for a in assets:
        part = a.partition or "?"
        lines.append(
            f"  - {a.name}: {a.host_path.name} ({a.size} bytes) → "
            f"0x{a.offset:x} (partition {part})"
        )
    lines.append(
        f"  esptool write_flash on {port} for each asset after idf flash "
        "(no hand-rolled offset essay required)."
    )
    return lines


def esptool_write_flash_args(
    *,
    port: str,
    chip: str,
    offset: int,
    file_path: Path,
) -> list[str]:
    """Argv *after* esptool prefix for one data write."""
    return [
        "--chip",
        chip,
        "--port",
        port,
        "write_flash",
        f"0x{offset:x}",
        str(file_path),
    ]
