# AGENTS.md

Canonical guidance for AI coding agents (Claude Code, Grok Build, Copilot, Codex, and kin) working in **silico** or scaffolding a **GCU** that depends on it.

Human overview: [README.md](README.md). Tenets: [specs/tenets.md](specs/tenets.md). Day 1 narrative: [specs/wb-2026-fall-three-gcus.md](specs/wb-2026-fall-three-gcus.md) FAQ 4. Build target: [specs/silicov1.md](specs/silicov1.md).

## What silico is

**Prompt for metal.** Open host-first spine for vertical edge products (GCUs). Not a company product line. Not the vertical domain app.

We work backwards from:

> With just Claude Code on my Mac, I had the device working end-to-end the next day, and in a potential customer's hand the day after that. Silico is now a foundational piece of our company's technology.

If a change does not make that sentence more true, it is not v1 work.

## Tenets (summary)

Full text: [specs/tenets.md](specs/tenets.md) (unless you know better ones).

1. **Software is not the moat.**
2. **Agents write the code.**
3. **Edge that just works is hard.**
4. **Vertical teams are the customer.**
5. **Prompt for metal.**
6. **Host first.**
7. **Apps stay apps.**
8. **Extract, then open.**

## Getting started for agents (Day 1)

When a human says: *See https://github.com/tig/silico. Follow the getting started instructions for agents.*

Run this playbook. Do not dump a wall of shell on the human. Confirm each phase with them before advancing.

### Phase A — Machine prerequisites

1. Detect OS (Windows / macOS / Linux).
2. Ensure **Git** is installed and on PATH.
3. Ensure **Python 3.9+** is installed (`py -3` on Windows, `python3` elsewhere).
4. Ensure **GitHub CLI (`gh`)** is installed. If missing, install via the OS package manager or official installer and verify `gh --version`.
5. Ensure **pip** works for that Python.
6. Report what you found/fixed. Stop if the human must click through an installer UI you cannot complete.

### Phase B — GitHub identity and GCU repo

1. Check `gh auth status`. If not logged in, guide the human through `gh auth login` (they complete the browser/device flow).
2. Ask: private GCU repo URL, or create new?
3. If create new:
   - Confirm product/codename for the repo name (not `silico`).
   - `gh repo create <name> --private --clone` (or create empty + push after scaffold).
4. If existing: clone or open that repo as the **workspace root for product work**.
5. Silico itself stays at `github.com/tig/silico`. The **product** lives in the private GCU repo.

### Phase C — Pin silico and scaffold the GCU

1. If the GCU is empty or not yet a silico plate, scaffold layout:

```text
<gcu>/
  AGENTS.md          # product agent guide (domain + pointer to silico tenets)
  CLAUDE.md          # stub → AGENTS.md
  firmware/          # on-device app only
  sim/               # host tests + plant; never deploy
  scripts/           # thin wrappers around silico host tools
  install/           # end-customer update docs
  requirements-dev.txt
  pytest.ini
  .github/workflows/ci.yml
  silico.toml        # product config when tools exist
```

2. Pin silico as a **host** dependency only:

```text
# requirements-dev.txt
silico @ git+https://github.com/tig/silico.git@main
# or while developing silico locally:
# -e /path/to/tig/silico
pytest>=8
mpy-cross>=1.20
```

3. `pip install -r requirements-dev.txt` (use the same Python as CI will use).
4. Add a minimal host CI workflow that runs the host gate (pytest; no COM port).
5. Commit and push. Confirm GitHub Actions (or equivalent) is enabled on the private repo.

Until silico ships a real installable package and plate generator, implement the thinnest plate that satisfies host-first: versioned firmware stub, pytest that fails closed if missing, deploy script stub that will call silico APIs when present.

### Phase D — Talk to real hardware (hello metal)

Goal: LEDs flash **green**, reconnect is **repeatable**, runtime installed once if needed.

1. Ask the human to plug the board via a **data** USB cable.
2. Prefer explicit port selection. On multi-device Windows hosts, do not trust blind `connect auto`. Prefer Raspberry Pi VID `2e8a`; demote CH340 `1a86` and Debug Probe `2e8a:000c`.
3. If no MicroPython REPL: guide BOOT+RESET → `RPI-RP2` → RPI_PICO UF2 (or board-appropriate image). Once per board.
4. Prove REPL: `import sys; print(sys.platform)` → expect `rp2` for RP2040-class.
5. Deploy a minimal firmware that drives status LED green (or documented hello pattern).
6. Unplug/replug and redeploy or soft-reset until reconnect is boring.
7. Document the update command in `install/` for tomorrow morning.

### Phase E — CI proves metal change

1. Prompt the human to create a GitHub Issue on the **GCU** repo, e.g. title: `Change the firmware to flash green/red`.
2. When the issue exists, implement it: firmware behavior change **and** host tests/CI green.
3. Open PR or push per repo convention. Wait for CI green.
4. Deploy to the board; human confirms LED behavior matches the issue.
5. Close the issue with a short note linking the commit/PR.

This is the first closed loop: **issue → agent → host gate → CI → metal**.

### Phase F — Domain work (still Day 1)

1. Human points at domain intent (docs, notes, rough brief). You do **not** invent the vertical moat.
2. Write or update detailed specs under `specs/` or product docs in the GCU.
3. Test-first: host unit/smoke tests and sim where applicable.
4. Implement `firmware/` behind HAL-style boundaries (no hardware at import; pure domain where possible).
5. Codify a staged plan as **cross-linked, tagged GitHub Issues** for proprietary work.
6. Host gate green locally before claiming done. Flash only confirms.
7. Push; CI matches local. Human change requests arrive as GitHub Issues.

### Day 1 exit criteria (before Day 2)

- [ ] Device works end-to-end on the bench.
- [ ] Host gate green locally and on GitHub.
- [ ] Device `FW_VERSION` matches host.
- [ ] One documented update command a non-expert can re-run.
- [ ] Silico pinned as host dependency (not a vendored script pile).
- [ ] `firmware/` is the only thing that must live on metal for the app.

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

Package code (`src/silico` or similar), plates, and CI for the spine are **in progress**. Prefer implementing toward [silicov1.md](specs/silicov1.md). Do not invent a second architecture.

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
3. Do not skip host gate or CI because metal "looked fine."
4. Do not use blind serial auto-connect on multi-device hosts.
5. Do not deploy host `sim/` or silico package modules to the board.
6. Do not claim external adoption or platform status without scoreboard evidence.
7. Do not rewrite PR titles, Grady quotes, or Tig quotes unless the human asks.
8. Do not start Arduino / multi-runtime work unless a GCU forces it (v2).

## Commands (host)

Until the package lands, discover what exists and keep the gate honest:

```text
# In GCU repo, after pin/install:
pytest -q

# Typical device ops (explicit port):
# mpremote connect COMx exec "import sys; print(sys.platform)"
# silico / scripts deploy + version verify (when implemented)
```

Prefer explicit `COMx` / `/dev/tty...` over `connect auto` when more than one serial device is present.

## When working in silico itself

1. Re-read `specs/` files you will edit before changing them.
2. Prefer surgical edits over rewriting whole docs.
3. Preserve human-owned wording (PR title, Grady quote, Tig quote).
4. Commit in small, reviewable steps when the human wants revision history.
5. Host gate for silico package code when it exists; docs-only changes need no metal.
