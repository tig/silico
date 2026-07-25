# Capture checklist — hero video footage

Record once, re-cut forever. Put finished clips in `docs/hero-video/footage/` (or edit `timeline.toml` to match your names).

## Capture tools (by beat)

| Beats | Tool | Why |
|-------|------|-----|
| Browser, terminal, agent TUI, CI | **[tig/mcec](https://github.com/tig/mcec)** drive + `record` | Reproducible, window/region GIF, agent-operable — see **[mcec.md](mcec.md)** |
| Desk product face + boot sound | Camera / phone | Real metal; MCEC cannot hear the board |
| Opening / end card | [build.py](build.py) from `docs/hero.jpg` | No capture |

Do **not** default to OBS for the onscreen path. MCEC is the intended driver/recorder; full playbook is [mcec.md](mcec.md).

**MCEC output is GIF** (default max ~60 s / take). Split long first-ship UI into multiple takes; [timeline.toml](timeline.toml) stitches and time-lapses. ffmpeg accepts `.gif` sources directly.

**Audio:** only the desk clip must include the boot sound. Onscreen GIFs are silent; the assembler does not need audio on those segments.

---

## Before you roll

1. **Clean start practice GCU:** for an honest Xuss first-ship capture, `tig/xuss` `main` tip should be the product-only clean start (see silico `AGENTS.md`). Reset only with operator go.
2. **MCEC controller:** stand up disposable MCP controller from a **tig/mcec** clone (`scripts/Generate-HeroGif.ps1`). Overlay **OFF** for this marketing cut. Details: [mcec.md](mcec.md).
3. **Quiet desktop:** Win+D before each take; large fonts in terminal; no secrets in frame.
4. **Clock truth:** note wall-clock when the agent start prompt is pasted (session t0). Fill `session_start_sec` / `session_end_sec` in `timeline.toml` from the log below.
5. **Surprising metal:** boot tone / LEDs on the desk clip — heads-up for anyone in the room.
6. **Emergency stop:** MCEC default `Ctrl+Alt+Shift+S` if a drive goes wrong.

---

## Expected clips

| File | Content | Source | Notes |
|------|---------|--------|--------|
| `01-gh-silico-getting-started.gif` | silico README → Getting Started → agent prompt | MCEC | Highlight prompt |
| `02-terminal-clone-and-prompt.gif` | clone xuss → cd → start agent → paste prompt | MCEC | Readable pacing |
| `03a-welcome.gif` | Stage 0a welcome skeleton | MCEC | Short; slow in timeline |
| `03b-agent-work.gif` (+ `03c…`) | First-ship body / gates | MCEC | Multiple ≤60 s takes |
| `04-desk-xuss-boot-demo.mp4` | Board boot + product face demo | Camera | **Keep audio** |
| `05-xuss-ci-green.gif` | tig/xuss CI green | MCEC | Hold on green |

Opening still: `docs/hero.jpg`. End card: generated.

Optional: same basenames with `.mp4` after `ffmpeg -i clip.gif … clip.mp4`.

---

## Mark human gates

When recording agent UI takes, start a **new MCEC `record`** (or mark wall-clock) at:

| Marker | Timeline speed |
|--------|----------------|
| Start gate (yes / adjust) | ~1× |
| Plug USB / wait-device (if on-screen prompt) | ~1× |
| Confirm board | ~1× |
| Confirm deploy | ~1× |
| Product-face observe | ~1× |

Agent-only stretches: separate takes with high `speed` in `timeline.toml` (20–60×).

---

## Session time log (fill while capturing)

```text
session_t0 (paste prompt or agent start): ____:____:____ local
welcome visible: +____ s
start gate answered: +____ s
host gate green: +____ s
board confirmed: +____ s
deploy done / face observed: +____ s
CI green on remote: +____ s
```

Copy offsets into each segment’s `session_start_sec` / `session_end_sec`.

---

## After capture

```text
cd docs/hero-video
python build.py --check-footage
python build.py
python build.py --placeholders   # smoke without real clips
```

Review `out/hero.mp4`. Adjust speeds and trims; re-run. Publish per [README.md](README.md).
