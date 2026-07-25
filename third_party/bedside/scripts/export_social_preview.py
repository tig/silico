#!/usr/bin/env python3
"""Export a GitHub repository social preview image.

GitHub recommends 1280x640 (2:1), PNG/JPG/GIF under 1 MB.
https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview

Usage:
  python scripts/export_social_preview.py
  python scripts/export_social_preview.py path/to/master.jpg
  python scripts/export_social_preview.py path/to/master.jpg -o docs/images/social-preview.jpg
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Pillow is required. Install with: pip install Pillow"
    ) from exc

# Repo root = parent of scripts/
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SRC = ROOT / "docs" / "images" / "social-preview-master.jpg"
DEFAULT_OUT = ROOT / "docs" / "images" / "social-preview.jpg"
GH_SIZE = (1280, 640)
MAX_BYTES = 1_000_000


def cover_resize(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Scale with cover fit, then center-crop to exact size."""
    tw, th = size
    scale = max(tw / im.width, th / im.height)
    nw = max(tw, int(round(im.width * scale)))
    nh = max(th, int(round(im.height * scale)))
    resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def export(src: Path, out: Path, quality: int = 90) -> Path:
    if not src.is_file():
        raise FileNotFoundError(f"Source image not found: {src}")

    im = Image.open(src).convert("RGB")
    frame = cover_resize(im, GH_SIZE)
    out.parent.mkdir(parents=True, exist_ok=True)

    q = quality
    while q >= 60:
        frame.save(out, "JPEG", quality=q, optimize=True)
        size = out.stat().st_size
        if size <= MAX_BYTES:
            print(f"Wrote {out} ({frame.size[0]}x{frame.size[1]}, {size} bytes, q={q})")
            return out
        q -= 5

    raise SystemExit(
        f"Could not get under {MAX_BYTES} bytes at {out} (last size {out.stat().st_size})"
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "src",
        nargs="?",
        type=Path,
        default=DEFAULT_SRC,
        help=f"Master art (default: {DEFAULT_SRC.relative_to(ROOT)})",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Output path (default: {DEFAULT_OUT.relative_to(ROOT)})",
    )
    p.add_argument(
        "-q",
        "--quality",
        type=int,
        default=90,
        help="JPEG quality start (default 90; steps down if over 1 MB)",
    )
    args = p.parse_args(argv)
    export(args.src.resolve(), args.output.resolve(), quality=args.quality)
    return 0


if __name__ == "__main__":
    sys.exit(main())
