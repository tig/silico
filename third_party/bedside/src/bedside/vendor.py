"""Vendor-copy helpers (no git submodule required)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

# Trees consumers need for contract + eval + optional CLI install from path.
VENDOR_TOP_LEVEL = (
    "contract",
    "surface",
    "eval",
    "src",
    "pyproject.toml",
    "LICENSE",
    "README.md",
)


def detect_pin(source: Path) -> str | None:
    """Best-effort commit SHA or tag if source is a git work tree."""
    try:
        out = subprocess.run(
            ["git", "-C", str(source), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return out.stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def vendor_copy(
    source: Path,
    dest: Path,
    *,
    include_src: bool = True,
) -> list[str]:
    """Copy bedside artifacts from source repo root into dest.

    Replaces dest if it exists. Returns list of relative names copied.
    """
    source = source.resolve()
    dest = dest.resolve()
    if not source.is_dir():
        raise FileNotFoundError(f"vendor source not a directory: {source}")
    if not (source / "contract").is_dir():
        raise FileNotFoundError(
            f"vendor source missing contract/: {source} "
            "(point at a tig/bedside checkout, not a random folder)"
        )

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    copied: list[str] = []
    for name in VENDOR_TOP_LEVEL:
        if name == "src" and not include_src:
            continue
        src_item = source / name
        if not src_item.exists():
            continue
        target = dest / name
        if src_item.is_dir():
            shutil.copytree(
                src_item,
                target,
                ignore=shutil.ignore_patterns(
                    "__pycache__",
                    "*.pyc",
                    ".pytest_cache",
                    "*.egg-info",
                    ".git",
                ),
            )
        else:
            shutil.copy2(src_item, target)
        copied.append(name)

    stamp = dest / "VENDOR.md"
    pin = detect_pin(source) or "unknown"
    stamp.write_text(
        f"# Vendored Bedside\n\n"
        f"- Source: `{source.as_posix()}`\n"
        f"- Pin (best effort): `{pin}`\n"
        f"- Refresh: re-run `bedside init --vendor-from <path> --force` "
        f"or copy the tree again; keep product fixtures outside this directory.\n",
        encoding="utf-8",
    )
    copied.append("VENDOR.md")
    return copied
