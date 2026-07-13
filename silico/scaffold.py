"""Scaffold a GCU plate from the versioned template tree."""

from __future__ import annotations

import shutil
from importlib import resources
from pathlib import Path


def plate_root() -> Path:
    """Return filesystem path to plates/gcu (package data or repo checkout)."""
    # Prefer package data after install
    try:
        root = resources.files("silico").joinpath("plates", "gcu")
        if root.is_dir():
            return Path(str(root))
    except Exception:
        pass
    # Repo checkout: silico/../plates/gcu or silico/plates/gcu
    here = Path(__file__).resolve().parent
    for cand in (here / "plates" / "gcu", here.parent / "plates" / "gcu"):
        if cand.is_dir():
            return cand
    raise FileNotFoundError("silico plate tree not found (plates/gcu)")


def scaffold(dest: Path, *, force: bool = False) -> list[str]:
    """Copy plate into dest. Refuses to clobber non-empty dest unless force."""
    dest = dest.resolve()
    src = plate_root()
    lines: list[str] = [f"Plate source: {src}", f"Destination: {dest}"]

    if dest.exists():
        remaining = [p for p in dest.iterdir() if p.name != ".git"]
        if remaining and not force:
            names = ", ".join(sorted(p.name for p in remaining)[:12])
            raise FileExistsError(
                f"destination not empty ({names}). Pass force=True / --force to merge, "
                "or scaffold into a new directory."
            )
    else:
        dest.mkdir(parents=True)

    copied = 0
    for path in src.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        target = dest / rel
        if target.exists() and not force:
            lines.append(f"skip existing: {rel}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        lines.append(f"wrote {rel}")
        copied += 1

    lines.append(f"Done. {copied} files written.")
    lines.append("Next: edit silico.toml / firmware/version.py, then: pytest -q")
    return lines
