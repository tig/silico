# Hero video script — silico × xuss first ship

Narrative for the README **hero video**: one end-to-end first ship of the [Xuss](https://github.com/tig/xuss) demo **GCU** (General Contact Unit — Silico’s term for one shippable edge product) using Silico’s host path.

**Goal:** a viewer who has never opened the repo sees *prompt → clone → agent → board talking → CI green* in a short cut, with an on-screen clock that measures **real first-ship elapsed time** (not how long the edited video runs).

**Assembly:** machine plan is [`timeline.toml`](timeline.toml). Build with [`build.py`](build.py). Capture notes: [`record.md`](record.md).

---

## Target runtime (edit)

| Layer | Aim |
|-------|-----|
| Finished video | ~90–150 seconds |
| Real first-ship session on clock | whatever it actually took (often tens of minutes; clock may run into hours) |
| Aspect | 16:9 (1920×1080 default) |

Tune segment `speed` / trims in `timeline.toml` after the first rough cut.

---

## Beats

### 1. Opening — `docs/hero.jpg`

- Full-frame still of the existing hero image (`docs/hero.jpg`).
- Optional soft title: **silico** / *Prompt to metal*.
- Clock visible at **0:00**.
- Hold ~2.5–3.5 s.

### 2. GitHub: silico Getting Started → copy the prompt

- Screen recording of [github.com/tig/silico](https://github.com/tig/silico) (or the README rendered locally).
- Scroll to **Getting Started** / **Step 3** (the agent start prompt).
- Pause; highlight or zoom the prompt block so it is obviously the thing to copy:

  ```md
  Read https://github.com/tig/silico's AGENTS.md. Follow the guidance there exactly. Stay in this product checkout.
  ```

- Clock advances only a little (browsing time), real-time or mild speed-up.

### 3. Terminal — clone xuss, start agent, paste prompt

- Clean terminal (or TUI shell) at a neutral home directory.
- Commands, readable at 1× (or slight speed-up between commands only):

  ```sh
  git clone https://github.com/tig/xuss
  cd xuss
  grok
  ```

- Paste the Silico start prompt into the agent.
- Cut before the long agent monologue; hand off to the next beat at first meaningful agent output if possible.

### 4. Welcome — slow for readability

- From the agent session recording: the **Stage 0a orientation** (`silico welcome` skeleton in chat).
- **Slow** so a viewer can read key lines (~2–3 s of *readable* on-screen time; use `speed < 1` in the timeline).
- Do **not** race past “what Silico is / this GCU / start gate next.”

### 5. First-ship body — time-lapse, slow on human acts

- Same session (or stitched session clips): Stage A→D as a **time-lapse**.
- **Slow to ~1× (or gentle slow-mo)** whenever the human must act:
  - start-gate / yes-adjust chooser
  - plug USB / board confirm
  - deploy overwrite confirm
  - product-face observe (“do you see/hear …?”)
- Fast through pure agent work (installs, scaffold, pytest green, long thinking).
- Prefer **many short segments** in `timeline.toml` (same file, different `in_sec`/`out_sec`/`speed`) over one opaque 30× clip.

### 6. Desk — xuss on metal

- Cutaway to the physical board on the desk (M5GO-class for Xuss).
- Soft-reset / boot: **product face** (status LEDs / boot sound) as documented for Xuss.
- Short human demo of the product face / core functionality (a few seconds of honest bench truth).
- **Keep audio** for boot tone and demo; announce in capture notes if the tone is long.
- Clock keeps running (metal confirm is still first-ship time).

### 7. GitHub — tig/xuss CI green

- Browser or `gh` UI on [tig/xuss](https://github.com/tig/xuss): default branch / latest run **green**.
- Hold long enough to read the check name (~2–3 s).

### 8. End card

- Dark brand card.
- Primary line: **https://github.com/tig/silico**
- Optional: *Prompt to metal.* / final clock freeze or hide clock.
- Hold ~3–4 s.

---

## What this is not

- Not a substitute for [AGENTS.md](../../AGENTS.md) (agents still load the full playbook).
- Not a claim that every host finishes in the on-screen wall time of the *video* — the **clock** is the honest duration.
- Not past-HEAD salvage theater: capture should be a real first ship (or an explicitly labeled rehearsal).

---

## README embed (after first good render)

Prefer a short poster + link, or a GitHub-hosted asset:

```md
[![Silico — prompt to metal (hero video)](docs/hero.jpg)](URL_TO_HERO_MP4)
```

Or HTML `<video>` when the host supports it. See [README.md](README.md) in this folder for publish options (release asset vs LFS vs external).
