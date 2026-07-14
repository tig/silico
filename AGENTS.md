# AGENTS.md

Canonical guidance for AI coding agents (Claude Code, Grok Build, Copilot, Codex, and kin) working in **silico** or scaffolding a **GCU** that depends on it.

Human overview: [README.md](README.md). Tenets: [specs/tenets.md](specs/tenets.md). Phrase book: [specs/lexicon.md](specs/lexicon.md). Day 1 narrative: [specs/wb-2026-fall-three-gcus.md](specs/wb-2026-fall-three-gcus.md) FAQ 4. Build target: [specs/silicov1.md](specs/silicov1.md).


## Agent context load path (read once)

Context is finite. **Do not** open every manners file into the active window.

| Priority | Open | Job | Skip when |
|----------|------|-----|-----------|
| 1 | This file (`AGENTS.md`) | Silico spine: Day 1 phases, silico CLI, plate, host/metal DoD | — |
| 2 | `bedside.toml` + contract path it names | Normative portable manners (nine principles) | Already summarized below and you are not changing manners |
| 3 | `BEDSIDE.md` | **Metal domain pack only** (COM, UF2, deploy identity) | Already in Day 1 metal sections of this file for the current step |
| — | `third_party/bedside/README.md`, vendored stub `AGENTS.md`/`BEDSIDE.md`, full `eval/` docs | Upstream product / scoring | Almost always — use `bedside doctor|eval|ask|step` instead of loading prose |
| — | Full FAQ / tenets | Strategy | Only when the task is doctrine, not a metal slice |

### Canonical owner (overlap map)

| Topic | Canonical owner | Silico may hold |
|-------|-----------------|-----------------|
| Nine principles, anti-patterns, portable persona | **tig/bedside** `contract/` | One short summary + pin (no kinder soft-fork) |
| Operator gates (`ask` / `step`) | **tig/bedside** surface + CLI | One short pointer here; agent host pickers OK if same contract |
| Day 1 phases, silico verbs, plate, mpy-cross, deploy manifest | **silico AGENTS** + code | Not bedside |
| COM / UF2 / board identity / metal deploy confirm | **silico BEDSIDE.md** domain pack + silico CLI | AGENTS Day 1 may point here; avoid full restatement |
| Eval rubric / fixtures | **tig/bedside** `eval/` | Run CLI; do not paste rubric into context |
| Product domain (idle, vehicle, …) | **GCU repo** | Never silico or bedside |

### Context budget rule

Prefer **tools that encode manners** (`silico doctor|wait-device|inspect|deploy`, `bedside doctor|eval|ask|step`) over re-loading essays. If two files say the same rule, follow the **canonical owner** and treat the other as a pointer.

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

## Help the operator (Bedside)

We follow **[Bedside](https://github.com/tig/bedside)**. Load rules per **Agent context load path** above — do not also dump the full vendored README into context.

- Pin / paths: [bedside.toml](bedside.toml)
- Contract (normative): [third_party/bedside/contract](third_party/bedside/contract)
- Metal domain notes only: [BEDSIDE.md](BEDSIDE.md)
- Vendor stamp: [third_party/bedside/VENDOR.md](third_party/bedside/VENDOR.md)

Summary (full contract is normative; do not soft-fork):

1. Assume low ops literacy, high judgment.
2. No wall of unexplained shell.
3. Prefer doing over instructing.
4. Human acts: explicit, one step, dumb-simple.
5. Own first-time setup from zero.
6. Own scary surfaces in plain language.
7. Confirm in their words before irreversible or physical steps.
8. Never leave them at a cliff.
9. Teach only what Day 2 requires.

Silico domain (metal / host path) details: **BEDSIDE.md** and Day 1 phases below. Host tools that encode manners: `silico doctor`, `wait-device`, `inspect`, `deploy --yes`, plus Bedside operator gates below.

Prove manners: `bedside doctor` and `bedside eval` (vendored fixtures include `operator-gate-ask` / `operator-gate-step`).

### Operator gates: `bedside ask` / `bedside step` (not multi-choice free text)

Do **not** restate long "how to ask the human" essays. Prefer tools:

| Gate | Tool | Example |
|------|------|---------|
| Structured choice / yes-no | `bedside ask` | start Day 1, confirm board identity, confirm deploy overwrite |
| One physical / browser act | `bedside step` | plug data cable, hold BOOT, approve OS dialog |

```text
bedside ask --id start-day1 --prompt "Start Day 1 on this machine?" --choices yes,adjust --default yes
bedside ask --id confirm-board --prompt "Is COM9 the product board for this session?" --choices yes,no --default no
bedside ask --id confirm-deploy --prompt "Overwrite device firmware on COM9 now?" --choices yes,no --default no
bedside step --id plug-usb --prompt "Plug a data USB cable into the board." --expect "Board power LED on or new COM in wait-device."
```

Exit codes (agents): **0** recommended path / step confirmed; **10** declined, other choice, or human still needed; **30** setup error.

**Also OK:** the agent product's **structured question UI** (pickers, `AskUserQuestion`, etc.) when it implements the same contract: one gate, recommended first, no multi-option free-text walls. Free text remains for open domain judgment only.

Non-interactive / CI: `--answer` on `ask`, `--confirm` / `--decline` / `--no-wait` on `step` (see `bedside ask --help`).

Violating Bedside on the operator path violates **Agents operate the host path**.

## Make it better than you found it (non-negotiable)

Anytime the path is rough and you had to **guess, correct, reverse, or research** something that a better doc, plate, script, error message, or small infra fix would have prevented for the **next** agent: do not leave that knowledge only in chat.

1. **Notice friction.** Wrong default port, missing UF2 step, bedside eval miss, Windows-only failure, tool flag that changed: if you stumbled, the next agent will too.
2. **Prefer a durable fix in the right repo.**
   - **Portable operator manners** (contract, surface patterns, CLI init/doctor/eval/ask/step, fixtures, rubric): file and/or fix on **tig/bedside**. Silico is customer 0.
   - **Metal host spine** (ports, deploy, GCU plate, Day 1 playbook specifics): fix in **tig/silico**.
   - **Product domain** (idle control, vehicle): fix in the **GCU** repo.
3. **If you cannot land the fix now, file an issue.**
   - Bedside: gh issue create -R tig/bedside ...
   - Silico: gh issue create -R tig/silico ...
   - Good issues: what you were doing, what went wrong, recovery, proposed change.
4. **Do not soft-fork Bedside principles** into a kinder local AGENTS section. Pin the contract; improve upstream.
5. **Do not invent a parallel spine** in the GCU to avoid filing upstream.

Leaving tribal recovery in chat only violates **Make it better than you found it**.

## Getting started for agents (Day 1)

When a human says: *See https://github.com/tig/silico. Follow the getting started instructions for agents.*

Run this playbook under **Help the operator**. Confirm each phase with them before advancing.

### Phase 0 - Welcome the operator (proactive, safe)

Be **proactive in a safe way.** Before the start gate, **do** read-only discovery so your welcome is grounded - do **not** wait for the human to ask whether Git exists.

**Allowed before start gate** (read-only / non-destructive):

- Detect OS; run `git --version`, Python version (`py -3` / `python3`), `gh --version`, `pip` check
- `gh auth status` (do not start `gh auth login` until after go, unless they already asked)
- Read product `README` / `spec.md` / workspace layout
- If silico is already installed: `silico version` / `silico doctor` (read-only port list is fine)
- List serial ports only as information - **do not** inspect/deploy metal or assume a board identity

**Not allowed before start gate:**

- Installing packages, changing PATH, scaffold, deploy, device writes
- Destructive git (reset --hard, force-push) unless the operator already ordered that work
- Walls of shell for the human to paste when you could run the check yourself

Then speak in plain language. Structure (tone may vary; skeleton may not):

1. **Welcome** to Silico.
2. **Role:** you are here to get their GCU shipped and will step them through it.
3. **What you know now** - product intent **and** machine readiness (what is already OK vs what will need install after go), including **whether a preferred USB board is already talking**.
4. **Next step** in one short sentence (the first *mutating* step after go). Frame Day 1 as **host plate + device talk** - not host-only.
5. **Start gate:** ask whether to start or adjust something. Prefer the agent product's **structured question UI** when available (not a multi-option free-text paragraph).

Example shape:

> Welcome to Silico. I'm here to get your GCU shipped and will step you through it all.
> Here's what I know now about what you want: …
> On this machine I already checked: Git OK, Python 3.12 OK, gh logged in; preferred board not on USB yet (only a CH340).
> The next step is scaffold the plate, get host tests green, then get the board talking over USB (REPL) before we write anything.
> Do you want me to start? Or should I adjust something?

Only after a clear **go** (or after applying their adjustments and re-confirming) may you begin **mutating** Phase A work (installs, scaffold, repo create, device paths).

**Anti-pattern:** promising to stop after host gate and "check back before we go near the board." Host gate is a checkpoint, not Day 1 done. After go, you drive through Phase D prep (USB talk + REPL) unless the operator explicitly defers metal.

### Phase A - Machine prerequisites

1. Detect OS (Windows / macOS / Linux). Tell them what you detected in one sentence.
2. Ensure **Git** is installed and on PATH. Install if missing; verify with a version command you run.
3. Ensure **Python 3.11+** (`py -3` on Windows, `python3` elsewhere). Install/guide if missing; do not assume `python` means 3. Do not install EOL 3.9/3.10 as the project floor.
4. Ensure **GitHub CLI (`gh`)** is installed. Install if missing; verify `gh --version`.
5. Ensure **pip** works for that same Python.
6. Summarize ready vs needs a human click. Stop cleanly if an installer UI requires them.

### Phase B - GitHub identity and GCU repo

1. Check `gh auth status`. If not logged in, walk them through `gh auth login` **one prompt at a time** (browser/device code). Do not assume they have used `gh` before.
2. Ask: use an existing private GCU repo URL, or create new? Offer defaults; do not require Git vocabulary.
3. If create new:
  - Confirm a product or codename for the repo name (not `silico`).
  - Create private repo with `gh` and clone, or create empty then push after scaffold.
4. If existing: clone or open that repo as the **workspace root for product work**.
5. Remind them: silico stays `github.com/tig/silico`; **their product** is the private GCU repo.

### Phase C - Pin silico and scaffold the GCU

**Do not hand-invent a parallel spine.** Use the package + plate.

1. Install silico on the host (prefer **tag**, not `@main`):

```text
# In GCU requirements-dev.txt (or pip install directly while bootstrapping):
tig-silico @ git+https://github.com/tig/silico.git@main  # pin tag v0.1.4+ once cut (not v0.1.3: name mismatch)
pytest>=8
mpy-cross==<pin matching device MicroPython major.minor — see below>
```

```text
python -m pip install -U pip
python -m pip install "tig-silico @ git+https://github.com/tig/silico.git@main" pytest
# Never: pip install silico  — unrelated PyPI package (issue #27).
# local extraction only:
# python -m pip install -e /path/to/tig/silico
```

If install fails, **stop**, say the pin is broken, and file/fix on `tig/silico`. Do **not** vendor host tooling into the GCU.

**mpy-cross pin (ABI) — Silico owns this chain:**

Product specs must **not** name a MicroPython version or hand-derive the PyPI pin. That is board/toolchain knowledge.

1. Plate defaults ship a **recent stable** PyPI `mpy-cross` as a starting point only.
2. After the board talks: `silico inspect --port COMx --apply-mpy-pin` — Silico reads device MicroPython, maps to an installable pin (including matching-minor rc when stable is missing on PyPI), and writes **both** `silico.toml` `[runtime].mpy_cross` and `requirements-dev.txt`.
3. Do **not** leave multi-line ABI essays in the product repo; re-run apply if the board firmware changes.
4. Packaging: install **`tig-silico`**, never bare `pip install silico` (unrelated PyPI package). Prefer tag `v0.1.4+` (name=`tig-silico`); `v0.1.3` and earlier declare `name=silico` and fail as `tig-silico@v0.1.3`.
5. `silico doctor` warns on ancient plate pins. Fix before claiming the host compile gate is honest.


2. Scaffold the plate (merge into existing GCU is OK; product `README.md` / `spec.md` are never overwritten):

```text
silico scaffold .
# empty dir also fine: silico scaffold ./my-gcu
# --force overwrites non-protected plate files only (not README/spec)
```

3. Set product identity in `firmware/version.py` and `silico.toml` (plate defaults are generic).
4. Run host gate until green: `python -m pytest -q` (or `silico doctor` then pytest).
5. Commit and push. Confirm CI/Actions is on. If the human must enable Actions, give exact clicks.
6. **Do not stop here.** Host gate green is a checkpoint. **Immediately continue into Phase D** (device USB talk + prep). Do not treat "I'll come back before the board" as the plan after scaffold unless the operator explicitly said to defer metal.

### Phase D - Talk to real hardware (hello metal)

**Required for Day 1 exit** (not optional polish). Goal: board **talks over USB**, is **prepped** (REPL when that is the runtime), then a **distinct, documented** blink/app; reconnect is **repeatable**.

Metal COM/UF2/identity/deploy rules live once in **[BEDSIDE.md](BEDSIDE.md)** (domain pack). Do not re-open the full Bedside contract README for this phase. Prefer tools: `silico wait-device`, `inspect`, `pull`, `deploy`, `monitor`, and `bedside ask` / `bedside step` for human gates.

#### Phase D0 - Device talks (prep) before any deploy plan

Until true, device is **not** prepped (details: BEDSIDE.md metal first-run + scary surfaces):

1. Preferred port appears after a **real** poll (`silico wait-device`, often `--timeout 300`) — or operator confirmed a named port after inspect.
2. `silico inspect --port COMx` proves REPL **or** you are walking UF2 first-flash once.
3. Operator confirmed **this port is the product board** this session (`bedside ask --id confirm-board …` or host structured UI; default **no** if unsure).
4. Only then: deploy plan → operator gate (`bedside ask --id confirm-deploy …`) → `--yes` write → `--verify` (optional `--verify-import main` is compile-not-import for boot modules; `--prune` / `--reset` as needed).

**If the board was missing at Phase 0:** after host gate, ask only for the data cable plug, then **immediately** run a long `wait-device` poll. Do not end the turn with "plug it in whenever" and no poll.

**Anti-pattern:** host gate green + "hardware later" with no wait-device/inspect/REPL proof.

**Phase D steps (order only — rules in BEDSIDE.md):**

1. Data cable (`bedside step --id plug-usb …` if they must act) → long `silico wait-device`.
2. `silico doctor` / `silico inspect --port COMx` → `bedside ask --id confirm-board …`.
3. No REPL → UF2 once (BOOT+RESET → `RPI-RP2`) → re-inspect until talk.
4. Optional backup: `silico pull <dir> --port COMx`.
5. Dry plan: `silico deploy --port COMx` (manifest / files) **without** `--yes` → `bedside ask --id confirm-deploy …` (recommended **no** until they mean it) → `--yes --verify` (and friends).
6. Optional: `silico monitor --port COMx --duration 10`.
7. Document `install/` leave-behind (BEDSIDE Day-2 one-liner + LED "good").


### Phase E - CI proves metal change

1. Ask the human to open a GitHub Issue on the **GCU** repo. Give them the exact title to paste, e.g. `Change the firmware blink pattern (distinct A vs B)`. If they do not know how to open an issue, give the UI path or create it with `gh` after they approve.
2. When the issue exists, implement it: firmware behavior change **and** host tests/CI green.
3. Push or PR. You watch CI; you fix red builds.
4. Deploy to the board **only after operator confirmation** again if overwriting; ask them only to confirm the blink pattern matches the issue.
5. Close the issue with a short note linking the commit/PR.

Closed loop: **issue → agent → host gate → CI → metal**.

### Phase F - Domain work (still Day 1)

1. Human points at domain intent (docs, notes, rough brief). You do **not** invent the vertical moat.
2. Write detailed specs, tests, and `firmware/` under test-first and host-first rules.
3. Staged plan as **cross-linked, tagged GitHub Issues** for proprietary work.
4. Host gate green locally before claiming done. Flash only confirms.
5. Push; CI matches local. Change requests arrive as GitHub Issues. Implement them without requiring the human to know git branches unless they want to.

#### Spec gaps (late step only)

While coding, you will find product `spec.md` items that are lacking, confusing, or wrong.

1. **Do not block the current slice** on rewriting the spec. Prefer configurable defaults, explicit assumptions in code/issue comments, and host tests.
2. Quietly note gaps (issue comment or checklist).
3. **Late step** — after the current issue's host gate is green, or at a phase boundary — prompt the operator: what was wrong/missing, a proposed edit, and ask whether to update the spec **now**.
4. Edit the product spec only after a clear **yes**.

### Day 1 exit criteria (before Day 2)

Metal bar detail: [BEDSIDE.md](BEDSIDE.md). Spine/DoD: layered table below.

- [ ] **Device talks over USB** (`silico inspect` / REPL) and was **prepped** (runtime once if needed).
- [ ] Device works end-to-end on the bench (hello-metal or app after confirmed deploy).
- [ ] Host gate green locally and on GitHub.
- [ ] Device `FW_VERSION` matches host.
- [ ] One documented update path (BEDSIDE Day-2 leave-behind).
- [ ] Silico pinned as host dependency.
- [ ] Operator helped through first flash/serial without assumed ops expertise.

**Not exit criteria:** host gate alone, scaffold alone, or deferred metal with no poll/inspect.

**Day 2:** same update path; unit to potential customer or field trial.

## Definition of done (layered)

Host-first is **not** host-only. Claims must name the layer they prove:

| Layer | Claim example | Required proof |
|-------|---------------|----------------|
| **Host** | Domain logic / sim / plate | Named host gate green (default: `pytest -q`). CI green if remote exists. |
| **Metal I/O** | Sensing or actuation on pins | Inject/measure on **named** pins (or harness signature), not only LED blink or version import. |
| **Vehicle / field** | Product acceptance on real plant | Product Appendix / field procedure; not bench buzz alone. |
| **Deployed** | Board runs this build | Device `FW_VERSION` matches host; optional harness OK. |
| **Issue fixed** | Ticket closed | Proof matching the issue's **stated layer**. CI green alone is not enough for a metal/vehicle claim. |

### HAL seam (Silico-owned pattern)

The host gate is only honest if domain firmware is host-importable and hardware stays behind a seam:

1. **Contract** (`firmware/hal.py`) — method surface; no `machine`.
2. **Device backend** (`firmware/hal_board.py` or product equivalent) — only modules listed in `silico.toml` `[hal].allow_machine` may import `machine`.
3. **Host double** (`sim/hal_double.py`) — same method names for pytest.
4. **main** — `init(hal=…)` / `tick`; no top-level hardware; boot only as `__main__`.

Enforce with `silico gate` (deploy-set CPython import + machine allowlist). Do not re-derive a private HAL shape per GCU when the plate already ships one.

### Forbidden closes

- Do **not** close a **P0 sensing/actuation** issue as done with only host/sim code if the device path is still a stub (`pass`, empty IRQ, no feed into the estimator). Either:
  1. land metal code that proves the pin path, or
  2. leave a **blocking metal follow-up** open (title/status makes metal-TODO obvious) and do not narrate the product as metal-ready.
- Do **not** mark vehicle/Appendix acceptance done without the vehicle procedure (or explicit defer with open tracker).
- Prefer issue titles like `host-done / metal-TODO` when splitting layers is honest.

Never treat "I flashed something" or "pytest green" as metal/vehicle done.

### Product path (shipped defaults, not test-local substitutes)

A host suite that injects convenient gains/plants while the metal build runs different constants can be green while the product is unusable. That is a **harness** failure.

1. Put shipped parameters in `firmware/defaults.py` (or `[host].product_defaults` in `silico.toml`) and deploy that module.
2. Domain code (`main`, control law) must **read** those defaults — not hard-code a parallel table.
3. At least one sim scenario must **actually load** the defaults module and drive the product path with those values **unmodified**. The check is AST-based: an import, an attribute access, or a dynamic load (`_load("defaults")`). Naming a test `product_path` or mentioning it in a docstring does **not** satisfy it — a gate a comment can pass is the same green-but-broken gate this rule exists to prevent.
4. Extra scenarios may override gains to explore edges — but zero scenarios on shipped defaults is a gate fail.
5. Control loops: include a closed-loop scenario on shipped defaults against the plant; **fail if the loop cannot reach setpoint**.

Check: `silico product-path` (also run from plate tests). Anti-pattern: "14 host tests green" where every test constructs the controller with literals absent from the config table.

## Repository layout (this repo: silico)

| Path | Role |
|------|------|
| `AGENTS.md` | This file (canonical agent guidance) |
| `CLAUDE.md` | Stub → here |
| `README.md` | Human entry |
| `silico/` | Installable host package + CLI + `plates/gcu` |
| `tests/` | Host tests for the package |
| `third_party/bedside/` | Vendored Bedside (contract, surface, eval, CLI); not a submodule |
| `bedside.toml` / `BEDSIDE.md` | Bedside pin + silico domain notes |
| `specs/tenets.md` | Tenets |
| `specs/wb-2026-fall-three-gcus.md` | v1 Working Backwards (PR + FAQ) |
| `specs/wb-2027-defacto-edge-spine.md` | Short 2027 aspiration |
| `specs/silicov1.md` | v1 build spec |
| `specs/gcu-codenames.md` | Public GCU codenames only |
| `specs/lexicon.md` | Phrase book |

Prefer [silicov1.md](specs/silicov1.md). Do not invent a second architecture.

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
# Install spine (tag pin) + vendored bedside CLI (from a silico checkout)
# Package: tig-silico. CLI: silico. Not `pip install silico` (unrelated PyPI name).
python -m pip install "tig-silico @ git+https://github.com/tig/silico.git@main"
# when working in this repo:
python -m pip install -e ".[dev]"
python -m pip install -e ./third_party/bedside

bedside doctor
bedside eval
# operator gates (use host structured UI when it matches this contract):
# bedside ask --id confirm-board --prompt "Is COMx the product board?" --choices yes,no --default no
# bedside ask --id confirm-deploy --prompt "Overwrite firmware on COMx now?" --choices yes,no --default no
# bedside step --id plug-usb --prompt "Plug a data USB cable." --expect "Board shows power / new COM."

silico doctor
silico wait-device
silico scaffold .
python -m pytest -q

silico inspect --port COMx
# plan only (no write); --port required; prefer silico.toml [deploy].core with no file args:
silico deploy --port COMx
# AFTER bedside ask (or equivalent) confirms identity + write:
silico deploy --port COMx --yes --verify
```

Always pass explicit `COMx` / `/dev/tty...` to deploy. Confirm device identity every session via `bedside ask` (or host picker), not chat multi-choice walls.

## When working in silico itself

1. Re-read `specs/` files you will edit before changing them.
2. Prefer surgical edits over rewriting whole docs.
3. Preserve human-owned wording (PR title, Grady quote, Tig quote).
4. Commit in small, reviewable steps when the human wants revision history.
5. Host gate for silico package code when it exists; docs-only changes need no metal.
6. Apply **Make it better than you found it** here first: doc and infra PRs in this repo beat issues when you already have write access.
