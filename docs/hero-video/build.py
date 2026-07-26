#!/usr/bin/env python3
"""Assemble the silico × xuss README hero video from timeline.toml + footage.

Requires ffmpeg on PATH. Stdlib only.

Examples:
  python build.py --placeholders   # smoke path without real clips
  python build.py --check-footage
  python build.py
  python build.py --timeline timeline.toml --dry-run
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_TIMELINE = ROOT / "timeline.toml"


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


@dataclass
class ClockCfg:
    enabled: bool = True
    x: str = "w-tw-48"
    y: str = "40"
    font_size: int = 40
    font_color: str = "white"
    box: bool = True
    box_color: str = "black@0.55"
    box_border_w: int = 12
    prefix: str = ""


@dataclass
class BrandCfg:
    title: str = "silico"
    tagline: str = "Prompt to metal."
    credit_url: str = "https://github.com/tig/silico"
    hero_image: str = "../hero.jpg"


@dataclass
class VideoCfg:
    width: int = 1920
    height: int = 1080
    fps: int = 30
    output: str = "out/hero.mp4"
    crf: int = 20
    preset: str = "medium"


@dataclass
class Segment:
    id: str
    kind: str  # still | clip | card
    source: str | None = None
    duration_sec: float | None = None
    in_sec: float | None = None
    out_sec: float | None = None
    speed: float = 1.0
    session_start_sec: float = 0.0
    session_end_sec: float = 0.0
    show_clock: bool = True
    keep_audio: bool = False
    title_overlay: bool = False
    lines: list[str] = field(default_factory=list)
    subtitle: str = ""
    note: str = ""


@dataclass
class Timeline:
    video: VideoCfg
    brand: BrandCfg
    clock: ClockCfg
    segments: list[Segment]
    path: Path


def load_timeline(path: Path) -> Timeline:
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    v = raw.get("video", {})
    b = raw.get("brand", {})
    c = raw.get("clock", {})
    video = VideoCfg(
        width=int(v.get("width", 1920)),
        height=int(v.get("height", 1080)),
        fps=int(v.get("fps", 30)),
        output=str(v.get("output", "out/hero.mp4")),
        crf=int(v.get("crf", 20)),
        preset=str(v.get("preset", "medium")),
    )
    brand = BrandCfg(
        title=str(b.get("title", "silico")),
        tagline=str(b.get("tagline", "Prompt to metal.")),
        credit_url=str(b.get("credit_url", "https://github.com/tig/silico")),
        hero_image=str(b.get("hero_image", "../hero.jpg")),
    )
    clock = ClockCfg(
        enabled=bool(c.get("enabled", True)),
        x=str(c.get("x", "w-tw-48")),
        y=str(c.get("y", "40")),
        font_size=int(c.get("font_size", 40)),
        font_color=str(c.get("font_color", "white")),
        box=bool(c.get("box", True)),
        box_color=str(c.get("box_color", "black@0.55")),
        box_border_w=int(c.get("box_border_w", 12)),
        prefix=str(c.get("prefix", "")),
    )
    segments: list[Segment] = []
    for i, s in enumerate(raw.get("segments", [])):
        sid = str(s.get("id") or f"seg{i}")
        kind = str(s.get("kind", "clip"))
        if kind not in ("still", "clip", "card"):
            raise SystemExit(f"segment {sid}: unknown kind={kind!r}")
        speed = float(s.get("speed", 1.0))
        if speed <= 0:
            raise SystemExit(f"segment {sid}: speed must be > 0")
        lines = s.get("lines") or []
        if isinstance(lines, str):
            lines = [lines]
        segments.append(
            Segment(
                id=sid,
                kind=kind,
                source=s.get("source"),
                duration_sec=_opt_float(s.get("duration_sec")),
                in_sec=_opt_float(s.get("in_sec")),
                out_sec=_opt_float(s.get("out_sec")),
                speed=speed,
                session_start_sec=float(s.get("session_start_sec", 0)),
                session_end_sec=float(s.get("session_end_sec", 0)),
                show_clock=bool(s.get("show_clock", True)),
                keep_audio=bool(s.get("keep_audio", False)),
                title_overlay=bool(s.get("title_overlay", False)),
                lines=[str(x) for x in lines],
                subtitle=str(s.get("subtitle", "")),
                note=str(s.get("note", "")),
            )
        )
    if not segments:
        raise SystemExit(f"no segments in {path}")
    return Timeline(video=video, brand=brand, clock=clock, segments=segments, path=path)


def _opt_float(v: object) -> float | None:
    if v is None:
        return None
    return float(v)


# ---------------------------------------------------------------------------
# ffmpeg helpers
# ---------------------------------------------------------------------------


def require_ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        raise SystemExit("ffmpeg not found on PATH. Install ffmpeg and retry.")
    return path


def probe_duration(ffmpeg: str, media: Path) -> float:
    """Return duration in seconds via ffprobe-compatible ffmpeg -i parse, or ffprobe."""
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        r = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "json",
                str(media),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if r.returncode == 0:
            data = json.loads(r.stdout or "{}")
            dur = float(data.get("format", {}).get("duration") or 0)
            if dur > 0:
                return dur
    # Fallback: ffmpeg -i stderr
    r = subprocess.run(
        [ffmpeg, "-i", str(media)],
        capture_output=True,
        text=True,
        check=False,
    )
    err = r.stderr or ""
    # Duration: 00:01:23.45
    import re

    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", err)
    if not m:
        raise SystemExit(f"could not probe duration: {media}")
    h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return h * 3600 + mi * 60 + s


def find_font() -> str | None:
    candidates = [
        Path(r"C:\Windows\Fonts\segoeui.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\calibri.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
        Path("/Library/Fonts/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/TTF/DejaVuSans.ttf"),
    ]
    for p in candidates:
        if p.is_file():
            return str(p).replace("\\", "/")
    return None


def esc_drawtext(s: str) -> str:
    """Escape text for ffmpeg drawtext filter."""
    return (
        s.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "\\%")
    )


def esc_fontfile(path: str) -> str:
    """Escape a font path for drawtext=fontfile= (Windows drive colon).

    ffmpeg on Windows needs either quotes + \\: or a double-escaped colon.
    Quoted form is reliable for both -vf and filter_script files.
    """
    inner = path.replace("\\", "/").replace(":", "\\:")
    return f"'{inner}'"


def vf_args(vf: str, script_path: Path) -> list[str]:
    """Prefer filter_script file so long graphs and Windows paths stay intact."""
    write_vf_script(vf, script_path)
    # filter_script:v is the video filter equivalent of -vf from a file
    return ["-filter_script:v", str(script_path)]


def scale_pad_vf(width: int, height: int) -> str:
    return (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=0x0a101c,"
        f"setsar=1"
    )


def clock_drawtext(
    clock: ClockCfg,
    session_start: float,
    session_end: float,
    out_duration: float,
    fontfile: str | None,
) -> str | None:
    """Burn session clock that maps output t in [0, out_duration] → session range."""
    if not clock.enabled or out_duration <= 0:
        return None
    # session_sec = start + t * (end - start) / out_duration
    span = session_end - session_start
    # Avoid div by zero: hold at session_start
    if abs(out_duration) < 1e-6:
        rate = 0.0
    else:
        rate = span / out_duration
    # ss expression in ffmpeg: session_start + t * rate
    ss = f"({session_start:.6f}+t*{rate:.9f})"
    # Format as M:SS (minutes may exceed 59) — matches script "0:00".
    # Literal colon between mins/secs must be \: inside the filtergraph.
    text_expr = (
        f"%{{eif\\:{ss}/60\\:d}}\\:"
        f"%{{eif\\:mod({ss}\\,60)\\:d\\:2}}"
    )
    if clock.prefix:
        text_expr = esc_drawtext(clock.prefix) + text_expr

    parts = [
        f"drawtext=text='{text_expr}'",
        f"x={clock.x}",
        f"y={clock.y}",
        f"fontsize={clock.font_size}",
        f"fontcolor={clock.font_color}",
        "expansion=normal",
    ]
    if fontfile:
        parts.append(f"fontfile={esc_fontfile(fontfile)}")
    if clock.box:
        parts.append("box=1")
        parts.append(f"boxcolor={clock.box_color}")
        parts.append(f"boxborderw={clock.box_border_w}")
    return ":".join(parts)


def run_ffmpeg(ffmpeg: str, args: list[str], dry_run: bool) -> None:
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", *args]
    if dry_run:
        print("DRY:", subprocess.list2cmdline(cmd))
        return
    # Show a short preview of the command (full -vf lines are huge).
    preview = []
    for a in cmd:
        if len(a) > 80:
            preview.append(a[:60] + "…")
        else:
            preview.append(a)
    print("+", subprocess.list2cmdline(preview[:16]), "..." if len(preview) > 16 else "")
    r = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip()
        if err:
            print(err, file=sys.stderr)
        raise SystemExit(f"ffmpeg failed ({r.returncode})")


def write_vf_script(vf: str, path: Path) -> Path:
    """Write a video filtergraph to a file (avoids Windows cmdline colon hell)."""
    path.write_text(vf, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Segment encode
# ---------------------------------------------------------------------------


def resolve_source(tl_dir: Path, source: str | None) -> Path | None:
    if not source:
        return None
    p = Path(source)
    if not p.is_absolute():
        p = (tl_dir / p).resolve()
    return p


def clip_source_duration(
    ffmpeg: str, path: Path, in_sec: float | None, out_sec: float | None
) -> float:
    full = probe_duration(ffmpeg, path)
    start = in_sec or 0.0
    end = out_sec if out_sec is not None else full
    if end <= start:
        raise SystemExit(f"{path.name}: out_sec ({end}) must be > in_sec ({start})")
    if start < 0 or start >= full:
        raise SystemExit(f"{path.name}: in_sec {start} out of range (duration {full:.2f})")
    return min(end, full) - start


def output_duration_for_segment(
    ffmpeg: str, seg: Segment, src: Path | None, placeholders: bool
) -> float:
    if seg.kind in ("still", "card"):
        if seg.duration_sec is None or seg.duration_sec <= 0:
            raise SystemExit(f"segment {seg.id}: duration_sec required")
        return float(seg.duration_sec)
    # clip
    if placeholders and (src is None or not src.is_file()):
        # Keep placeholder slates short even when real tape trims are long.
        return 3.0
    assert src is not None
    raw = clip_source_duration(ffmpeg, src, seg.in_sec, seg.out_sec)
    return raw / seg.speed


def make_placeholder_clip(
    ffmpeg: str,
    out: Path,
    *,
    width: int,
    height: int,
    fps: int,
    duration: float,
    label: str,
    fontfile: str | None,
    dry_run: bool,
) -> None:
    """Generate a labeled color slate used when footage is missing."""
    # Use source duration = duration (speed already applied by caller? for placeholders
    # we generate final-length segment video).
    vf_parts = [
        f"scale={width}:{height}",
        "setsar=1",
    ]
    dt = (
        f"drawtext=text='{esc_drawtext(label)}':"
        f"x=(w-tw)/2:y=(h-th)/2:fontsize=48:fontcolor=white:"
        f"box=1:boxcolor=black@0.45:boxborderw=16"
    )
    if fontfile:
        dt += f":fontfile={esc_fontfile(fontfile)}"
    vf_parts.append(dt)
    vf = ",".join(vf_parts)
    script = out.with_suffix(".vf.txt")
    run_ffmpeg(
        ffmpeg,
        [
            "-f",
            "lavfi",
            "-i",
            f"color=c=0x123048:s={width}x{height}:d={duration:.4f}:r={fps}",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=48000",
            *vf_args(vf, script),
            "-t",
            f"{duration:.4f}",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            str(out),
        ],
        dry_run,
    )


def encode_segment(
    ffmpeg: str,
    tl: Timeline,
    seg: Segment,
    out_path: Path,
    *,
    fontfile: str | None,
    placeholders: bool,
    dry_run: bool,
) -> Path:
    v = tl.video
    tl_dir = tl.path.parent
    src = resolve_source(tl_dir, seg.source)

    if seg.kind == "card":
        return _encode_card(ffmpeg, tl, seg, out_path, fontfile, dry_run)

    if seg.kind == "still":
        return _encode_still(ffmpeg, tl, seg, out_path, fontfile, dry_run, src)

    # clip
    missing = src is None or not src.is_file()
    if missing and not placeholders:
        raise SystemExit(
            f"segment {seg.id}: missing footage {seg.source!r}. "
            f"Record it (see record.md) or pass --placeholders."
        )

    out_dur = output_duration_for_segment(ffmpeg, seg, src, placeholders=missing)
    if missing:
        # Labeled slate at final output duration, then burn session clock.
        tmp = out_path.with_suffix(".pre.mp4")
        make_placeholder_clip(
            ffmpeg,
            tmp if not dry_run else out_path,
            width=v.width,
            height=v.height,
            fps=v.fps,
            duration=out_dur,
            label=f"{seg.id} (placeholder)",
            fontfile=fontfile,
            dry_run=dry_run,
        )
        if dry_run:
            return out_path
        _reclock(
            ffmpeg,
            tmp,
            out_path,
            tl,
            seg,
            out_dur,
            fontfile,
            keep_audio=False,
            dry_run=dry_run,
        )
        tmp.unlink(missing_ok=True)
        return out_path

    assert src is not None and src.is_file()
    raw = clip_source_duration(ffmpeg, src, seg.in_sec, seg.out_sec)

    # Inputs first (ffmpeg option order), then maps / filters / codecs.
    args: list[str] = []
    if seg.in_sec is not None:
        args.extend(["-ss", f"{seg.in_sec:.4f}"])
    args.extend(["-i", str(src)])
    if not seg.keep_audio:
        args.extend(
            [
                "-f",
                "lavfi",
                "-i",
                "anullsrc=channel_layout=stereo:sample_rate=48000",
            ]
        )

    # speed S means play S× faster → setpts = PTS/S
    setpts = f"setpts=PTS/{seg.speed}"
    vf = f"{scale_pad_vf(v.width, v.height)},fps={v.fps},{setpts}"
    if seg.show_clock and tl.clock.enabled:
        clock_f = clock_drawtext(
            tl.clock, seg.session_start_sec, seg.session_end_sec, out_dur, fontfile
        )
        if clock_f:
            vf = f"{vf},{clock_f}"
    args.extend(vf_args(vf, out_path.with_suffix(".vf.txt")))

    # Trim source read length (pre-speed); setpts shortens the output timeline.
    args.extend(["-t", f"{raw:.4f}"])

    if seg.keep_audio:
        atempo = _atempo_filters(seg.speed)
        if atempo:
            args.extend(["-af", atempo])
        args.extend(["-map", "0:v:0", "-map", "0:a:0?"])
    else:
        args.extend(["-map", "0:v:0", "-map", "1:a:0", "-shortest"])

    args.extend(
        [
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            v.preset,
            "-crf",
            str(v.crf),
            "-r",
            str(v.fps),
            "-c:a",
            "aac",
            "-ar",
            "48000",
            "-ac",
            "2",
            str(out_path),
        ]
    )
    run_ffmpeg(ffmpeg, args, dry_run)
    return out_path


def _atempo_filters(speed: float) -> str | None:
    """Return atempo filter chain for playback speed S (S>1 faster)."""
    if abs(speed - 1.0) < 1e-6:
        return None
    # atempo is tempo factor = speed (play faster → higher tempo)
    factors: list[float] = []
    remaining = speed
    # Clamp each stage to [0.5, 2.0]
    if remaining > 1:
        while remaining > 2.0 + 1e-9:
            factors.append(2.0)
            remaining /= 2.0
        factors.append(remaining)
    else:
        while remaining < 0.5 - 1e-9:
            factors.append(0.5)
            remaining /= 0.5
        factors.append(remaining)
    return ",".join(f"atempo={f:.6f}" for f in factors)


def _reclock(
    ffmpeg: str,
    src: Path,
    out: Path,
    tl: Timeline,
    seg: Segment,
    out_dur: float,
    fontfile: str | None,
    *,
    keep_audio: bool,
    dry_run: bool,
) -> None:
    vf = scale_pad_vf(tl.video.width, tl.video.height)
    if seg.show_clock and tl.clock.enabled:
        clock_f = clock_drawtext(
            tl.clock, seg.session_start_sec, seg.session_end_sec, out_dur, fontfile
        )
        if clock_f:
            vf = f"{vf},{clock_f}"
    args = [
        "-i",
        str(src),
        "-f",
        "lavfi",
        "-i",
        "anullsrc=channel_layout=stereo:sample_rate=48000",
        *vf_args(vf, out.with_suffix(".vf.txt")),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0" if not keep_audio else "0:a:0?",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        tl.video.preset,
        "-crf",
        str(tl.video.crf),
        "-r",
        str(tl.video.fps),
        "-c:a",
        "aac",
        "-ar",
        "48000",
        "-ac",
        "2",
        "-t",
        f"{out_dur:.4f}",
        "-shortest",
        str(out),
    ]
    run_ffmpeg(ffmpeg, args, dry_run)


def _encode_still(
    ffmpeg: str,
    tl: Timeline,
    seg: Segment,
    out_path: Path,
    fontfile: str | None,
    dry_run: bool,
    src: Path | None,
) -> Path:
    v = tl.video
    dur = float(seg.duration_sec or 3.0)
    if src is None or not src.is_file():
        # solid fallback
        make_placeholder_clip(
            ffmpeg,
            out_path,
            width=v.width,
            height=v.height,
            fps=v.fps,
            duration=dur,
            label=tl.brand.title,
            fontfile=fontfile,
            dry_run=dry_run,
        )
        if not dry_run and seg.show_clock:
            tmp = out_path.with_suffix(".tmp.mp4")
            out_path.rename(tmp)
            _reclock(
                ffmpeg,
                tmp,
                out_path,
                tl,
                seg,
                dur,
                fontfile,
                keep_audio=False,
                dry_run=dry_run,
            )
            tmp.unlink(missing_ok=True)
        return out_path

    vf = scale_pad_vf(v.width, v.height)
    # optional title overlay on open
    if seg.title_overlay:
        title = esc_drawtext(tl.brand.title)
        tag = esc_drawtext(tl.brand.tagline)
        t1 = (
            f"drawtext=text='{title}':x=80:y=h-180:fontsize=64:"
            f"fontcolor=0x40c4ff:box=1:boxcolor=black@0.4:boxborderw=14"
        )
        t2 = (
            f"drawtext=text='{tag}':x=80:y=h-100:fontsize=32:"
            f"fontcolor=white:box=1:boxcolor=black@0.4:boxborderw=10"
        )
        if fontfile:
            t1 += f":fontfile={esc_fontfile(fontfile)}"
            t2 += f":fontfile={esc_fontfile(fontfile)}"
        vf = f"{vf},{t1},{t2}"
    if seg.show_clock and tl.clock.enabled:
        clock_f = clock_drawtext(
            tl.clock, seg.session_start_sec, seg.session_end_sec, dur, fontfile
        )
        if clock_f:
            vf = f"{vf},{clock_f}"

    run_ffmpeg(
        ffmpeg,
        [
            "-loop",
            "1",
            "-i",
            str(src),
            "-f",
            "lavfi",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=48000",
            *vf_args(vf, out_path.with_suffix(".vf.txt")),
            "-t",
            f"{dur:.4f}",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            v.preset,
            "-crf",
            str(v.crf),
            "-r",
            str(v.fps),
            "-c:a",
            "aac",
            "-shortest",
            str(out_path),
        ],
        dry_run,
    )
    return out_path


def _encode_card(
    ffmpeg: str,
    tl: Timeline,
    seg: Segment,
    out_path: Path,
    fontfile: str | None,
    dry_run: bool,
) -> Path:
    v = tl.video
    dur = float(seg.duration_sec or 4.0)
    lines = seg.lines or [tl.brand.credit_url]
    primary = esc_drawtext(lines[0])
    sub = esc_drawtext(seg.subtitle or tl.brand.tagline)
    t1 = (
        f"drawtext=text='{primary}':x=(w-tw)/2:y=(h-th)/2-20:fontsize=44:"
        f"fontcolor=0x40c4ff:box=1:boxcolor=black@0.35:boxborderw=18"
    )
    t2 = (
        f"drawtext=text='{sub}':x=(w-tw)/2:y=(h-th)/2+60:fontsize=28:"
        f"fontcolor=0xd2dce0"
    )
    if fontfile:
        t1 += f":fontfile={esc_fontfile(fontfile)}"
        t2 += f":fontfile={esc_fontfile(fontfile)}"
    vf = f"setsar=1,{t1},{t2}"
    if seg.show_clock and tl.clock.enabled:
        clock_f = clock_drawtext(
            tl.clock, seg.session_start_sec, seg.session_end_sec, dur, fontfile
        )
        if clock_f:
            vf = f"{vf},{clock_f}"

    run_ffmpeg(
        ffmpeg,
        [
            "-f",
            "lavfi",
            "-i",
            f"color=c=0x0a101c:s={v.width}x{v.height}:d={dur:.4f}:r={v.fps}",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=48000",
            *vf_args(vf, out_path.with_suffix(".vf.txt")),
            "-t",
            f"{dur:.4f}",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            v.preset,
            "-crf",
            str(v.crf),
            "-c:a",
            "aac",
            "-shortest",
            str(out_path),
        ],
        dry_run,
    )
    return out_path


def concat_segments(
    ffmpeg: str,
    parts: list[Path],
    out: Path,
    *,
    crf: int,
    preset: str,
    dry_run: bool,
) -> None:
    """Concat demuxer; re-encode once for clean A/V alignment."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        list_path = Path(f.name)
        for p in parts:
            # concat demuxer needs escaped single quotes in paths
            ap = p.resolve().as_posix().replace("'", "'\\''")
            f.write(f"file '{ap}'\n")
    try:
        run_ffmpeg(
            ffmpeg,
            [
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_path),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-preset",
                preset,
                "-crf",
                str(crf),
                "-c:a",
                "aac",
                "-movflags",
                "+faststart",
                str(out),
            ],
            dry_run,
        )
    finally:
        list_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def check_footage(tl: Timeline) -> int:
    tl_dir = tl.path.parent
    missing = []
    present = []
    for seg in tl.segments:
        if seg.kind != "clip" or not seg.source:
            continue
        p = resolve_source(tl_dir, seg.source)
        if p and p.is_file():
            present.append(str(p.relative_to(tl_dir) if p.is_relative_to(tl_dir) else p))
        else:
            missing.append(seg.source)
    print(f"clips present: {len(present)}")
    for p in present:
        print(f"  OK  {p}")
    print(f"clips missing: {len(missing)}")
    for m in missing:
        print(f"  --  {m}")
    return 1 if missing else 0


def plan_summary(tl: Timeline, ffmpeg: str | None, placeholders: bool) -> None:
    print(f"timeline: {tl.path}")
    print(f"output:   {tl.video.output}  ({tl.video.width}x{tl.video.height}@{tl.video.fps})")
    total_out = 0.0
    session_hi = 0.0
    for seg in tl.segments:
        src = resolve_source(tl.path.parent, seg.source)
        try:
            if ffmpeg:
                od = output_duration_for_segment(ffmpeg, seg, src, placeholders)
            else:
                od = float(seg.duration_sec or 0) if seg.kind != "clip" else 0.0
        except SystemExit as e:
            od = 0.0
            print(f"  ! {seg.id}: {e}")
        total_out += od
        session_hi = max(session_hi, seg.session_end_sec)
        print(
            f"  - {seg.id:20} kind={seg.kind:5} speed={seg.speed:g} "
            f"out≈{od:6.2f}s  clock {seg.session_start_sec:.0f}→{seg.session_end_sec:.0f}s  "
            f"{'(audio)' if seg.keep_audio else ''}"
        )
        if seg.note:
            print(f"      note: {seg.note}")
    print(f"approx video length: {total_out:.1f}s")
    print(f"session clock end:   {session_hi:.0f}s ({session_hi/60:.1f} min)")


def build(
    tl: Timeline,
    *,
    placeholders: bool,
    dry_run: bool,
    keep_segments: bool,
) -> Path:
    ffmpeg = require_ffmpeg()
    fontfile = find_font()
    if fontfile:
        print(f"font: {fontfile}")
    else:
        print("font: (default ffmpeg font — install a TTF if text looks wrong)")

    plan_summary(tl, ffmpeg, placeholders)

    out_rel = Path(tl.video.output)
    out_path = out_rel if out_rel.is_absolute() else (tl.path.parent / out_rel)
    seg_dir = out_path.parent / "segments"
    if not dry_run:
        seg_dir.mkdir(parents=True, exist_ok=True)
        out_path.parent.mkdir(parents=True, exist_ok=True)

    parts: list[Path] = []
    for i, seg in enumerate(tl.segments):
        part = seg_dir / f"{i:02d}_{seg.id}.mp4"
        print(f"\n=== segment {seg.id} → {part.name} ===")
        encode_segment(
            ffmpeg,
            tl,
            seg,
            part,
            fontfile=fontfile,
            placeholders=placeholders,
            dry_run=dry_run,
        )
        parts.append(part)

    print(f"\n=== concat → {out_path} ===")
    concat_segments(
        ffmpeg,
        parts,
        out_path,
        crf=tl.video.crf,
        preset=tl.video.preset,
        dry_run=dry_run,
    )
    if not dry_run and not keep_segments:
        # keep segments by default for re-edit; only delete if asked? keep them.
        pass
    if not dry_run:
        size = out_path.stat().st_size if out_path.is_file() else 0
        print(f"\nWrote {out_path} ({size / 1_000_000:.2f} MB)")
    return out_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build silico README hero video")
    ap.add_argument(
        "--timeline",
        type=Path,
        default=DEFAULT_TIMELINE,
        help="path to timeline.toml",
    )
    ap.add_argument(
        "--placeholders",
        action="store_true",
        help="synthesize missing clips as labeled slates (pipeline smoke)",
    )
    ap.add_argument(
        "--check-footage",
        action="store_true",
        help="list present/missing clip sources and exit",
    )
    ap.add_argument(
        "--plan",
        action="store_true",
        help="print segment plan only (no encode)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="print ffmpeg commands without running",
    )
    ap.add_argument(
        "--keep-segments",
        action="store_true",
        default=True,
        help="keep out/segments/*.mp4 (default: true)",
    )
    args = ap.parse_args(argv)

    path = args.timeline.resolve()
    if not path.is_file():
        print(f"timeline not found: {path}", file=sys.stderr)
        return 2

    tl = load_timeline(path)

    if args.check_footage:
        return check_footage(tl)

    if args.plan:
        ff = shutil.which("ffmpeg")
        plan_summary(tl, ff, placeholders=args.placeholders)
        return 0

    build(
        tl,
        placeholders=args.placeholders,
        dry_run=args.dry_run,
        keep_segments=args.keep_segments,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
