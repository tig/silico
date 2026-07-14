"""Build GitHub social preview image (1280x640, <1MB).

GitHub docs (customizing repository social media preview):
- PNG, JPG, or GIF under 1 MB
- At least 640x320; **1280x640 recommended** for best display
- Prefer a solid background (transparency can look odd in dark mode)

Template layout used here (common Open Graph / GH social card pattern):
- Canvas 1280x640 (exact 2:1)
- ~64px safe margins so crops on Slack/Twitter/LinkedIn keep title + hero
- Brand title + tagline in a card inside the safe zone
- Optional repo identity bottom-left
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# GitHub social preview recommended canvas
W, H = 1280, 640
MARGIN = 64  # keep primary content inside platform crop-safe area

ROOT = Path(__file__).resolve().parent
# Prefer clean base (no baked-in text); fall back to hero.jpg
SRC_CANDIDATES = (ROOT / "hero-clean.jpg", ROOT / "hero.jpg")
OUT_JPG = ROOT / "social-preview.jpg"
OUT_PNG = ROOT / "social-preview.png"


def load_font(names: list[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def rounded_rect(
    draw: ImageDraw.ImageDraw,
    box: list[int],
    r: int,
    fill: tuple[int, ...],
    outline: tuple[int, ...] | None = None,
    width: int = 2,
) -> None:
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def center_crop_2x1(src: Image.Image, width: int, height: int) -> Image.Image:
    """Crop source to target aspect (2:1) then resize to exact pixels."""
    sw, sh = src.size
    target_ratio = width / height
    src_ratio = sw / sh
    if src_ratio > target_ratio:
        new_w = int(sh * target_ratio)
        left = (sw - new_w) // 2
        crop = src.crop((left, 0, left + new_w, sh))
    else:
        new_h = int(sw / target_ratio)
        # Bias slightly up so laptop + board stay in frame
        top = max(0, (sh - new_h) // 2 - 20)
        if top + new_h > sh:
            top = sh - new_h
        crop = src.crop((0, top, sw, top + new_h))
    return crop.resize((width, height), Image.Resampling.LANCZOS)


def main() -> None:
    src_path = next(p for p in SRC_CANDIDATES if p.is_file())
    src = Image.open(src_path).convert("RGB")
    canvas = center_crop_2x1(src, W, H)
    draw = ImageDraw.Draw(canvas)

    title_font = load_font(
        [
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\calibrib.ttf",
        ],
        64,
    )
    tag_font = load_font(
        [
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\calibri.ttf",
        ],
        28,
    )
    repo_font = load_font(
        [
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arial.ttf",
        ],
        22,
    )

    title = "silico"
    tag = "Prompt for metal."
    title_color = (64, 196, 255)
    tag_color = (210, 220, 235)

    # Layout with anchor="lt" (left-top) so height is ink-box only — no baseline bleed
    pad_x, pad_y = 32, 32
    gap_title_line = 16
    gap_line_tag = 16
    line_h = 1

    title_bb = draw.textbbox((0, 0), title, font=title_font, anchor="lt")
    tag_bb = draw.textbbox((0, 0), tag, font=tag_font, anchor="lt")
    title_w, title_h = title_bb[2] - title_bb[0], title_bb[3] - title_bb[1]
    tag_w, tag_h = tag_bb[2] - tag_bb[0], tag_bb[3] - tag_bb[1]

    content_w = max(title_w, tag_w)
    content_h = title_h + gap_title_line + line_h + gap_line_tag + tag_h
    card_w = max(content_w + 2 * pad_x, 360)
    card_h = content_h + 2 * pad_y

    card_x1 = W - MARGIN
    card_x0 = card_x1 - card_w
    card_y0 = MARGIN
    card_y1 = card_y0 + card_h
    card_box = [card_x0, card_y0, card_x1, card_y1]
    rounded_rect(
        draw,
        card_box,
        r=16,
        fill=(12, 22, 38),
        outline=(40, 90, 140),
        width=2,
    )

    tx = card_x0 + pad_x
    title_y = card_y0 + pad_y
    draw.text((tx, title_y), title, font=title_font, fill=title_color, anchor="lt")

    line_y = title_y + title_h + gap_title_line
    draw.line(
        [(tx, line_y), (card_x1 - pad_x, line_y)],
        fill=(40, 90, 140),
        width=line_h,
    )
    tag_y = line_y + line_h + gap_line_tag
    draw.text((tx, tag_y), tag, font=tag_font, fill=tag_color, anchor="lt")

    tag_bottom = tag_y + tag_h
    assert tag_bottom + pad_y <= card_y1 + 1, (
        f"tag bleeds: bottom={tag_bottom} card_y1={card_y1} pad={pad_y}"
    )
    print(f"card {card_w}x{card_h}; tag bottom {tag_bottom}, card bottom {card_y1}")

    # Bottom-left repo identity inside safe margin
    repo = "github.com/tig/silico"
    bbox = draw.textbbox((0, 0), repo, font=repo_font, anchor="lt")
    rw, rh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pill_pad_x, pill_pad_y = 12, 10
    rx = MARGIN
    ry = H - MARGIN - rh - pill_pad_y
    pill = [
        rx - pill_pad_x,
        ry - pill_pad_y,
        rx + rw + pill_pad_x,
        ry + rh + pill_pad_y,
    ]
    rounded_rect(
        draw,
        pill,
        r=10,
        fill=(10, 16, 28),
        outline=(30, 50, 70),
        width=1,
    )
    draw.text((rx, ry), repo, font=repo_font, fill=(160, 180, 200), anchor="lt")

    canvas.save(OUT_JPG, "JPEG", quality=90, optimize=True, progressive=True)
    size = OUT_JPG.stat().st_size
    print(f"source: {src_path.name}")
    print(f"JPEG: {OUT_JPG.name} {canvas.size} {size / 1024:.1f} KB")

    if size > 1_000_000:
        for q in (85, 80, 75, 70):
            canvas.save(OUT_JPG, "JPEG", quality=q, optimize=True, progressive=True)
            size = OUT_JPG.stat().st_size
            print(f"  recompress q={q}: {size / 1024:.1f} KB")
            if size <= 1_000_000:
                break

    canvas.save(OUT_PNG, "PNG", optimize=True)
    psize = OUT_PNG.stat().st_size
    print(f"PNG:  {OUT_PNG.name} {psize / 1024:.1f} KB")
    if psize > 1_000_000:
        OUT_PNG.unlink()
        print("PNG >1MB removed; use JPEG for GitHub upload")

    print(f"Safe content margins: {MARGIN}px on all sides")
    print("Upload: repo Settings → Social preview → Edit → Upload an image")


if __name__ == "__main__":
    main()
