# Hero video (README)

Reproduce the **silico × xuss** end-to-end hero cut for the root [README](../../README.md).

| File | Role |
|------|------|
| [SCRIPT.md](SCRIPT.md) | Narrative beats (what the viewer should see) |
| [record.md](record.md) | How to capture each source clip |
| [timeline.toml](timeline.toml) | Edit decision list: order, trims, speed, session clock |
| [build.py](build.py) | ffmpeg assembler (clock burn-in, stills, cards, concat) |
| `footage/` | Your recordings (gitignored binaries) |
| `out/` | Rendered `hero.mp4` (gitignored) |

## Prerequisites

- **ffmpeg** on `PATH` (`ffmpeg -version`)
- **Python 3.11+** (stdlib only: `tomllib`, `argparse`, `subprocess`, …)
- Source clips under `footage/` **or** use `--placeholders` to smoke the pipeline

Optional: a font ffmpeg can find for `drawtext` (Windows: `C:\\Windows\\Fonts\\segoeui.ttf`; macOS: Helvetica; Linux: DejaVu). The builder probes common paths.

## Quick start

```text
# From repo root or this directory:
python docs/hero-video/build.py --placeholders
python docs/hero-video/build.py --check-footage
python docs/hero-video/build.py
```

Outputs:

- `docs/hero-video/out/hero.mp4` — final cut
- `docs/hero-video/out/segments/` — intermediate segment encodes (debug)

## Clock semantics

The on-screen timer is **first-ship session elapsed**, not video wall-clock.

Each segment maps its **output** duration linearly from `session_start_sec` → `session_end_sec`. Time-lapse (`speed = 30`) advances the clock quickly; slow-mo (`speed = 0.35`) holds readable moments while session time still creeps.

Fill session times from the log in [record.md](record.md) after a real capture.

## Editing workflow

1. Record clips per [record.md](record.md).
2. Set `in_sec` / `out_sec` / `speed` on each `[[segments]]` entry in `timeline.toml`.
3. Split the long agent tape into **gate-slow** vs **timelapse** segments (examples commented in the timeline).
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
- Placeholders keep the assemble path testable without committing multi‑hundred‑MB screen captures.
- No soft-fork of Bedside or first-ship manners: the video *shows* the path; [AGENTS.md](../../AGENTS.md) remains normative for agents.
