"""Host tests for docs/hero-video assembler (no product domain)."""

from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
BUILD_PY = REPO / "docs" / "hero-video" / "build.py"
TIMELINE = REPO / "docs" / "hero-video" / "timeline.toml"


def _load_build():
    spec = importlib.util.spec_from_file_location("hero_video_build", BUILD_PY)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["hero_video_build"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def hv():
    return _load_build()


def test_timeline_loads_and_has_script_beats(hv):
    tl = hv.load_timeline(TIMELINE)
    ids = [s.id for s in tl.segments]
    assert ids[0] == "open"
    assert "welcome-slow" in ids
    assert "desk-metal" in ids
    assert "ci-green" in ids
    assert ids[-1] == "credits"
    assert tl.brand.credit_url.startswith("https://github.com/tig/silico")
    assert tl.clock.enabled
    # Onscreen path is MCEC GIF (desk remains camera mp4).
    by_id = {s.id: s for s in tl.segments}
    assert by_id["gh-scroll"].source.endswith(".gif")
    assert by_id["terminal-start"].source.endswith(".gif")
    assert by_id["welcome-slow"].source.endswith(".gif")
    assert by_id["ci-green"].source.endswith(".gif")
    assert by_id["desk-metal"].source.endswith(".mp4")


def test_clock_drawtext_maps_session_range(hv):
    clock = hv.ClockCfg()
    f = hv.clock_drawtext(clock, 120.0, 180.0, 10.0, fontfile=None)
    assert f is not None
    assert "drawtext=" in f
    assert "120" in f
    # rate = (180-120)/10 = 6
    assert "6" in f or "6.0" in f


def test_atempo_chains_for_extreme_speed(hv):
    assert hv._atempo_filters(1.0) is None
    fast = hv._atempo_filters(30.0)
    assert fast is not None
    assert "atempo=" in fast
    slow = hv._atempo_filters(0.35)
    assert slow is not None


def test_check_footage_reports_missing(hv):
    tl = hv.load_timeline(TIMELINE)
    code = hv.check_footage(tl)
    # Fresh clone has no recorded clips
    assert code == 1


def test_plan_does_not_require_footage(hv, capsys):
    tl = hv.load_timeline(TIMELINE)
    hv.plan_summary(tl, ffmpeg=None, placeholders=True)
    out = capsys.readouterr().out
    assert "open" in out
    assert "session clock end" in out


def test_mcec_playbook_exists():
    mcec = REPO / "docs" / "hero-video" / "mcec.md"
    text = mcec.read_text(encoding="utf-8")
    assert "tig/mcec" in text
    assert "record" in text
    assert "Generate-HeroGif.ps1" in text
    assert "AgentRecordMaxDurationMs" in text or "60 s" in text


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not on PATH")
def test_placeholder_build_smoke(hv, tmp_path):
    """Encode a tiny placeholder cut into tmp (validates ffmpeg filter graph)."""
    # Minimal timeline: open still + credits card only
    mini = tmp_path / "timeline.toml"
    hero = REPO / "docs" / "hero.jpg"
    mini.write_text(
        f"""
[video]
width = 640
height = 360
fps = 15
output = "out/hero.mp4"
crf = 28
preset = "ultrafast"

[brand]
title = "silico"
tagline = "Prompt to metal."
credit_url = "https://github.com/tig/silico"
hero_image = "{hero.as_posix()}"

[clock]
enabled = true
font_size = 24

[[segments]]
id = "open"
kind = "still"
source = "{hero.as_posix()}"
duration_sec = 0.4
session_start_sec = 0
session_end_sec = 0
show_clock = true
title_overlay = true

[[segments]]
id = "slate"
kind = "clip"
source = "footage/missing.mp4"
speed = 1.0
session_start_sec = 0
session_end_sec = 30
show_clock = true

[[segments]]
id = "credits"
kind = "card"
duration_sec = 0.4
session_start_sec = 30
session_end_sec = 30
show_clock = false
lines = ["https://github.com/tig/silico"]
subtitle = "Prompt to metal."
""",
        encoding="utf-8",
    )
    tl = hv.load_timeline(mini)
    # Rewrite output under tmp
    tl.video.output = str((tmp_path / "out" / "hero.mp4").as_posix())
    out = hv.build(tl, placeholders=True, dry_run=False, keep_segments=True)
    assert out.is_file()
    assert out.stat().st_size > 1000
