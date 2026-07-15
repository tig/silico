"""Scaffold a GCU plate from the versioned template tree."""

from __future__ import annotations

import shutil
from importlib import resources
from pathlib import Path

# Product identity - never overwrite even with --force.
PROTECTED_NAMES = frozenset(
    {
        "README.md",
        "spec.md",
        "LICENSE",
        "LICENSE.md",
    }
)

SKIP_DIR_NAMES = frozenset({"__pycache__", ".git", ".pytest_cache", ".venv", "venv"})
SKIP_SUFFIXES = frozenset({".pyc", ".pyo"})


def plate_root() -> Path:
    """Return filesystem path to plates/gcu (package data or repo checkout)."""
    try:
        root = resources.files("silico").joinpath("plates", "gcu")
        if root.is_dir():
            return Path(str(root))
    except Exception:
        pass
    here = Path(__file__).resolve().parent
    for cand in (here / "plates" / "gcu", here.parent / "plates" / "gcu"):
        if cand.is_dir():
            return cand
    raise FileNotFoundError("silico plate tree not found (plates/gcu)")


def _should_skip_source(rel: Path) -> bool:
    """Skip decision on the path RELATIVE to the plate root.

    Never test the absolute source path: when silico is pip-installed into a
    venv that lives inside the destination repo (the layout the Day 1 playbook
    itself produces), every plate file's absolute path contains ".venv" as a
    part and the whole plate is silently skipped (tig/silico#48).
    """
    if any(part in SKIP_DIR_NAMES for part in rel.parts):
        return True
    if rel.suffix in SKIP_SUFFIXES:
        return True
    return False


def scaffold(dest: Path, *, force: bool = False) -> list[str]:
    """Merge plate into dest.

    Default: add missing plate files; skip existing files (safe for product README/spec).
    --force: overwrite non-protected existing plate files.
    Protected (never overwritten): README.md, spec.md, LICENSE.
    """
    dest = dest.resolve()
    src = plate_root()
    fresh = not (dest / "silico.toml").exists()
    lines: list[str] = [
        f"Plate source: {src}",
        f"Destination: {dest}",
        "Merge mode: skip existing files"
        + ("; --force overwrites non-protected plate files" if force else ""),
        f"Protected (never overwrite): {', '.join(sorted(PROTECTED_NAMES))}",
    ]

    if not dest.exists():
        dest.mkdir(parents=True)

    copied = 0
    skipped = 0
    protected = 0
    for path in sorted(src.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        if _should_skip_source(rel):
            continue
        target = dest / rel
        name = path.name

        if target.exists():
            if name in PROTECTED_NAMES or str(rel).replace("\\", "/") in PROTECTED_NAMES:
                lines.append(f"protect product: {rel}")
                protected += 1
                continue
            if not force:
                lines.append(f"skip existing: {rel}")
                skipped += 1
                continue

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        lines.append(f"wrote {rel}")
        copied += 1

    lines.append(
        f"Done. {copied} written, {skipped} skipped (existing), {protected} protected."
    )
    if copied == 0 and fresh:
        lines.append(
            "WARN: wrote nothing on a fresh destination (no silico.toml) — a "
            "fresh scaffold that writes zero files is never what the operator "
            "meant. See tig/silico#48."
        )
    lines.append("Next: set firmware/version.py + silico.toml product names, then: pytest -q")
    return lines
