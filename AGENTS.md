# AGENTS.md

Canonical guidance for AI coding agents (Claude Code, Grok Build, Copilot, Codex, and kin) working in **silico** or scaffolding a **GCU** that depends on it.

Human overview: [README.md](README.md). Tenets: [specs/tenets.md](specs/tenets.md). Phrase book: [specs/lexicon.md](specs/lexicon.md). Day 1 narrative: [specs/wb-2026-fall-three-gcus.md](specs/wb-2026-fall-three-gcus.md) FAQ 4. Build target: [specs/silicov1.md](specs/silicov1.md).

## What silico is

**Prompt for metal.** Open host-first spine for vertical edge products (GCUs). Not a company product line. Not the vertical domain app.

We work backwards from:

> With just Claude Code on my Mac, I had the device working end-to-end the next day, and in a potential customer's hand the day after that. Silico is now a foundational piece of our company's technology.

If a change does not make that sentence more true, it is not v1 work.

## Tenets (summary)

Full text: [specs/tenets.md](specs/tenets.md) (unless you know better ones).

1. **Software is not the moat.**
2. **Agents write the code.**
3. **Agents operate the host path.**
4. **Make it better than you found it.**
5. **Edge that just works is hard.**
6. **Vertical teams are the customer.**
7. **Prompt for metal.**
8. **Host first.**
9. **Apps stay apps.**
10. **Extract, then open.**

## Help the operator (non-negotiable)

The human is often **Grady-shaped**: domain or hardware judgment, not a software or embedded expert. Your job is to **help the operator**, not to examine them.

1. **Assume low ops literacy.** Do not assume they know Git, GitHub, Python, pip, COM ports, UF2, bootloader buttons, or your tool's slash-commands.
2. **Do not dump a wall of shell.** Never paste five unexplained commands and say "run these." One step at a time. Say what it does, then run it yourself when you can.
3. **Prefer doing over instructing.** If you can install `gh`, create a repo, run pytest, or call `mpremote`, do it. Only hand the human steps that require their body: browser login, plugging USB, holding BOOT, approving a UAC prompt, reading an LED.
4. **When the human must act, be explicit and dumb-simple.**
   - Name the exact app/window if relevant.
   - Give the physical action: "Hold the button labeled BOOT on the board, tap RESET, then release BOOT."
   - Give the exact string to paste if they must type something you cannot run.
   - Do **not** assume they know agent UI tricks (for example typing `! xyz` to run a host command, approving a tool, or opening a terminal profile). Explain the click path once.
5. **First firmware is your problem.** Do not assume the board already has MicroPython or that they know how to get initial firmware on the device. Detect blank vs REPL. Walk UF2 or the board's first-flash path from zero. Once per board, then never make them re-learn it for app updates.
6. **Serial is scary; own it.** List candidate ports in plain language ("likely the board", "likely a different adapter"). Prefer explicit ports. If something fails, say what you will try next; do not shame them for cable/port confusion.
7. **Confirm understanding in their words.** Before an irreversible or physical step, one short check: "You should see a drive named RPI-RP2. Do you?"
8. **Never leave them at a cliff.** If you are blocked (need a password, need a click), say exactly what you need and wait. Do not continue as if they finished.
9. **Teach only what Day 2 requires.** After success, leave one documented update command and where the LED should look. No textbook.

Violating this section violates **Agents operate the host path**.

## Make it better than you found it (non-negotiable)

Anytime the path is rough and you had to **guess, correct, reverse, or research** something that a better `AGENTS.md`, plate, script, error message, or small infra fix would have prevented for the **next** agent: do not leave that knowledge only in chat.

1. **Notice friction.** Wrong default port, missing UF2 step, CI secret gotcha, ambiguous prompt, Windows-only failure, tool flag that changed: if you stumbled, the next agent will too.
2. **Prefer a durable fix in silico.**
   - Edit `AGENTS.md` or other agent-facing docs when the gap is guidance.
   - Fix or extend host tooling when the gap is code (when that code lives in silico).
   - Keep product domain fixes in the **GCU** repo; keep spine/agent-path fixes in **tig/silico**.
3. **If you cannot land the fix now, file an issue on `tig/silico`.** Use `gh issue create` in the silico repo (or ask the operator to open one if you lack permission). Good issues include:
   - What you were trying to do (Day 1 phase or task).
   - What went wrong (exact error or wrong assumption).
   - What you did to recover.
   - Proposed doc or code change so the next agent does not guess.
4. **Tag when useful.** e.g. `agents`, `day-1`, `host-path`, `docs`, `bug`.
5. **Mention the issue** in the PR or session summary so humans see the trail.
6. **Do not "helpfully" invent a parallel spine** in the GCU to avoid filing upstream. Pin silico; improve silico.

Leaving tribal recovery in chat only violates **Make it better than you found it**.

## Getting started for agents (Day 1)

When a human says: *See https://github.com/tig/silico. Follow the getting started instructions for agents.*

Run this playbook under **Help the operator**. Confirm each phase with them before advancing.

### Phase A — Machine prerequisites

1. Detect OS (Windows / macOS / Linux). Tell them what you detected in one sentence.
2. Ensure **Git** is installed and on PATH. Install if missing; verify with a version command you run.
3. Ensure **Python 3.11+** (`py -3` on Windows, `python3` elsewhere). Install/guide if missing; do not assume `python` means 3. Do not install EOL 3.9/3.10 as the project floor.
4. Ensure **GitHub CLI (`gh`)** is installed. Install if missing; verify `gh --version`.
5. Ensure **pip** works for that same Python.
6. Summarize ready vs needs a human click. Stop cleanly if an installer UI requires them.

### Phase B — GitHub identity and GCU repo

1. Check `gh auth status`. If not logged in, walk them through `gh auth login` **one prompt at a time** (browser/device code). Do not assume they have used `gh` before.
2. Ask: use an existing private GCU repo URL, or create new? Offer defaults; do not require Git vocabulary.
3. If create new:
   - Confirm a product or codename for the repo name (not `silico`).
   - Create private repo with `gh` and clone, or create empty then push after scaffold.
4. If existing: clone or open that repo as the **workspace root for product work**.
5. Remind them: silico stays `github.com/tig/silico`; **their product** is the private GCU repo.

### Phase C — Pin silico and scaffold the GCU

1. If the GCU is empty or not yet a silico plate, scaffold:

```text
<gcu>/
  AGENTS.md          # product agent guide (domain + silico tenets pointer)
  CLAUDE.md          # stub → AGENTS.md
  firmware/          # on-device app only
  sim/               # host tests + plant; never deploy
  scripts/           # thin wrappers around silico host tools
  install/           # end-customer update docs (plain language)
  requirements-dev.txt
  pytest.ini
  .github/workflows/ci.yml
  silico.toml        # product config when tools exist
```

2. Pin silico as a **host** dependency only (you edit the file; you run pip). Prefer an **immutable tag or commit SHA**, not `@main` (version identity doctrine):

```text
# requirements-dev.txt — use a release tag when one exists
silico @ git+https://github.com/tig/silico.git@v0.1.0
# local extraction / pre-package:
# -e /path/to/tig/silico
pytest>=8
# mpy-cross must match the device MicroPython runtime (pin exact version in silico.toml when set)
mpy-cross==1.22.2
```

If `pip install` of the git pin fails because the package is not installable yet, stop and say so: pre-alpha. Use path install only while extracting; do not invent a vendored spine in the GCU.

3. Install host deps with **Python 3.11+** (same as CI will use). Fix failures yourself when possible.
4. Add minimal host CI (pytest; no COM port).
5. Commit and push. Confirm Actions (or equivalent) is on. If the human must enable Actions in the GitHub UI, give exact clicks; do not assume they know where Settings is.

Until silico ships a real package and plate generator, implement the thinnest plate that satisfies host-first: versioned firmware stub, pytest that fails closed if missing, deploy path that will call silico APIs when present.

### Phase D — Talk to real hardware (hello metal)

Goal: board shows a **distinct, documented blink pattern** a novice can recognize (color LED if present; otherwise clear on/off timing), reconnect is **repeatable**, runtime on board once if needed.

1. Ask them to use a **data** USB cable (not charge-only). Explain that some cables only power.
2. Have them plug the board. You list serial candidates in plain language; pick explicit port. On multi-device Windows, never rely on blind `connect auto`. Prefer VID `2e8a`; demote CH340 `1a86` and Debug Probe `2e8a:000c`.
3. If no MicroPython REPL: **you** drive first firmware. Step-by-step physical: hold BOOT, tap RESET, release BOOT → wait for `RPI-RP2` drive → download/copy the correct UF2 → wait for reconnect. Do not assume they have ever done this. Once per board.
4. Prove REPL yourself: `import sys; print(sys.platform)` → `rp2` for RP2040-class. Tell them what "good" looks like.
5. Deploy minimal firmware with the hello blink pattern; document what “good” looks like.
6. Unplug/replug with them until reconnect is boring.
7. Write `install/` in plain language for tomorrow morning (one command, what the board should look like).

### Phase E — CI proves metal change

1. Ask the human to open a GitHub Issue on the **GCU** repo. Give them the exact title to paste, e.g. `Change the firmware blink pattern (distinct A vs B)`. If they do not know how to open an issue, give the UI path or create it with `gh` after they approve.
2. When the issue exists, implement it: firmware behavior change **and** host tests/CI green.
3. Push or PR. You watch CI; you fix red builds.
4. Deploy to the board; ask them only to confirm the blink pattern matches the issue.
5. Close the issue with a short note linking the commit/PR.

Closed loop: **issue → agent → host gate → CI → metal**.

### Phase F — Domain work (still Day 1)

1. Human points at domain intent (docs, notes, rough brief). You do **not** invent the vertical moat.
2. Write detailed specs, tests, and `firmware/` under test-first and host-first rules.
3. Staged plan as **cross-linked, tagged GitHub Issues** for proprietary work.
4. Host gate green locally before claiming done. Flash only confirms.
5. Push; CI matches local. Change requests arrive as GitHub Issues. Implement them without requiring the human to know git branches unless they want to.

### Day 1 exit criteria (before Day 2)

- [ ] Device works end-to-end on the bench.
- [ ] Host gate green locally and on GitHub.
- [ ] Device `FW_VERSION` matches host.
- [ ] One documented update command a non-expert can re-run (you wrote the doc).
- [ ] Silico pinned as host dependency.
- [ ] Operator was helped through first flash and serial without assumed expertise.

**Day 2:** same update path; unit to potential customer or field trial.

## Definition of done

| Claim | Required proof |
|-------|----------------|
| `firmware/` change done | Named host gate green (default: `pytest -q` or project AGENTS command). CI green if remote exists. |
| Deployed | Device version matches host; optional harness OK. |
| Issue fixed | CI green **and** metal behavior matches the issue. |

Never treat "I flashed something" as done.

## Repository layout (this repo: silico)

| Path | Role |
|------|------|
| `AGENTS.md` | This file (canonical agent guidance) |
| `CLAUDE.md` | Stub → here |
| `README.md` | Human entry |
| `specs/tenets.md` | Tenets |
| `specs/wb-2026-fall-three-gcus.md` | v1 Working Backwards (PR + FAQ) |
| `specs/wb-2027-defacto-edge-spine.md` | Short 2027 aspiration |
| `specs/silicov1.md` | v1 build spec |
| `specs/gcu-codenames.md` | Public GCU codenames only |

Package code, plates, and spine CI are **in progress**. Prefer [silicov1.md](specs/silicov1.md). Do not invent a second architecture.

## GCU vs silico

| | **silico** (`tig/silico`) | **GCU** (private product repo) |
|--|---------------------------|--------------------------------|
| Owner | Open spine | Vertical product |
| On metal | No | `firmware/` yes |
| Host pin | N/A (is the package) | `requirements-dev.txt` pins silico |
| Domain IP | Never | Always |
| Public codenames | Zakalwe, Quilan, Sma only | Real brands stay private |

When a second GCU needs the same host machinery, promote into silico and bump the pin (**Extract, then open**).

## Confidentiality

Starter products are confidential. In public silico docs and commits use **Zakalwe**, **Quilan**, **Sma** only. Do not expand codenames to real brands, customers, or markets.

## What not to do

1. Do not put product domain logic into silico to win a demo.
2. Do not require the human to hand-author firmware as the default path.
3. Do not assume the human can flash initial firmware, pick ports, or run agent/shell tricks without being taught in the moment.
4. Do not dump unexplained command walls; do not say "run this" when you could run it.
5. Do not skip host gate or CI because metal "looked fine."
6. Do not use blind serial auto-connect on multi-device hosts.
7. Do not deploy host `sim/` or silico package modules to the board.
8. Do not claim external adoption or platform status without scoreboard evidence.
9. Do not rewrite PR titles, Grady quotes, or Tig quotes unless the human asks.
10. Do not start Arduino / multi-runtime work unless a GCU forces it (v2).
11. Do not burn an hour recovering from silico friction and leave no issue or doc fix for the next agent.

## Commands (host)

Run these yourself when possible. Show the human only what they must see.

```text
# In GCU repo, after pin/install:
pytest -q

# Device ops: always explicit port after you explain which one
# mpremote connect COMx exec "import sys; print(sys.platform)"
```

Prefer explicit `COMx` / `/dev/tty...` over `connect auto` when more than one serial device is present.

## When working in silico itself

1. Re-read `specs/` files you will edit before changing them.
2. Prefer surgical edits over rewriting whole docs.
3. Preserve human-owned wording (PR title, Grady quote, Tig quote).
4. Commit in small, reviewable steps when the human wants revision history.
5. Host gate for silico package code when it exists; docs-only changes need no metal.
6. Apply **Make it better than you found it** here first: doc and infra PRs in this repo beat issues when you already have write access.
