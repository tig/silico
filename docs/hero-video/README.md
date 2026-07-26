# Hero video (README)

Reproduce the **silico × xuss** end-to-end hero cut for the root [README](../../README.md).

| File | Role |
|------|------|
| [SCRIPT.md](SCRIPT.md) | Narrative beats (what the viewer should see) |
| [mcec.md](mcec.md) | **Onscreen drive + record** with [tig/mcec](https://github.com/tig/mcec) |
| [record.md](record.md) | Capture checklist (MCEC vs desk camera) |
| [timeline.toml](timeline.toml) | Edit decision list: order, trims, speed, session clock |
| [build.py](build.py) | ffmpeg assembler (clock burn-in, stills, cards, concat) |
| `footage/` | MCEC GIFs + desk MP4 (gitignored binaries) |
| `out/` | Rendered `hero.mp4` (gitignored) |

## Prerequisites

- **Windows** host for onscreen takes (MCEC is Windows-only computer use)
- **[tig/mcec](https://github.com/tig/mcec)** controller via `scripts/Generate-HeroGif.ps1` from a mcec clone (see [mcec.md](mcec.md))
- **ffmpeg** on `PATH`
- **Python 3.11+** (stdlib only for `build.py`)
- Source clips under `footage/` **or** `--placeholders` to smoke the pipeline

Optional: a font ffmpeg can find for `drawtext` (Windows Segoe UI, etc.).

## Quick start

```text
# 1) Capture onscreen with MCEC (playbook):
#    docs/hero-video/mcec.md

# 2) Assemble:
python docs/hero-video/build.py --placeholders
python docs/hero-video/build.py --check-footage
python docs/hero-video/build.py
```

Outputs:

- `docs/hero-video/out/hero.mp4` — final cut
- `docs/hero-video/out/segments/` — intermediate segment encodes (debug)

## Capture model

```text
  MCEC (drive + record GIF)          Camera
  ├─ browser silico README           └─ desk xuss boot / product face
  ├─ terminal clone + agent start
  ├─ agent welcome + staged first ship
  └─ browser xuss CI green
           │
           ▼
  footage/*  →  build.py + timeline.toml  →  out/hero.mp4
```

MCEC `record` is **GIF**, typically **≤60 s** per take unless you raise controller limits. Long first-ship UI is **multiple takes**; the timeline time-lapses them. Session clock in the final video is still real first-ship elapsed time (`session_*_sec`).

## Clock semantics

The on-screen timer is **first-ship session elapsed**, not video wall-clock.

Each segment maps its **output** duration linearly from `session_start_sec` → `session_end_sec`. Time-lapse (`speed = 30`) advances the clock quickly; slow-mo (`speed = 0.35`) holds readable moments while session time still creeps.

Fill session times from the log in [record.md](record.md) after a real capture.

## Editing workflow

1. Capture onscreen with MCEC per [mcec.md](mcec.md); desk clip with a camera.
2. Drop files into `footage/`; set `in_sec` / `out_sec` / `speed` in `timeline.toml`.
3. Split agent UI into **gate-slow** vs **timelapse** segments.
4. `python build.py` → review → tweak → repeat.
5. Publish the mp4 (see below) and point the root README at it.

## Publish options

Raw `hero.mp4` is usually too large for a normal git blob. Prefer:

1. **GitHub Release asset** on `tig/silico` (or a `hero-video` release tag), then link from README with the hero still as poster.
2. **GitHub issue/PR drag-upload** URL (convenient for drafts; less stable than a release).
3. **Git LFS** only if the team already standardizes on LFS for media.

Suggested README shape once hosted:

```md
[![Silico — prompt to metal](docs/hero.jpg)](https://github.com/tig/silico/releases/download/hero-video/hero.mp4)

*Hero video: first ship of [Xuss](https://github.com/tig/xuss) with Silico. Reproduce: [docs/hero-video](docs/hero-video).*
```

## Design notes

- Same spirit as `docs/_make_social_preview.py`: **docs tooling in-tree**, not product domain in the spine.
- Onscreen path **composes** with [tig/mcec](https://github.com/tig/mcec) (drive + `record`); silico does not vendor MCEC.
- Placeholders keep the assemble path testable without committing large captures.
- No soft-fork of Bedside or first-ship manners: the video *shows* the path; [AGENTS.md](../../AGENTS.md) remains normative for agents.
