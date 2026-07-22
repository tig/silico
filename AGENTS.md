# AGENTS.md

Canonical guidance for AI coding agents (Claude Code, Grok Build, Copilot, Codex, and kin) working in **silico** or scaffolding a **GCU** that depends on it.

Human overview: [README.md](README.md). Tenets: [specs/tenets.md](specs/tenets.md). Phrase book: [specs/lexicon.md](specs/lexicon.md). Day 1 narrative: [specs/wb-2026-fall-three-gcus.md](specs/wb-2026-fall-three-gcus.md) FAQ 4. Build target: [specs/silicov1.md](specs/silicov1.md).


## Agent context load path (read once)

Context is finite. **Do not** open every manners file into the active window.

| Priority | Open | Job | Skip when |
|----------|------|-----|-----------|
| 1 | This file (`AGENTS.md`) | Silico spine: Day 1 phases, silico CLI, plate, host/metal DoD | — |
| 2 | `bedside.toml` + contract path it names | Normative portable manners (nine principles) | Already summarized below and you are not changing manners |
| 3 | `BEDSIDE.md` | **Metal domain pack only** (COM, first-flash, deploy identity) | Already in Day 1 metal sections of this file for the current step |
| 4 | One topic under `silico/knowledge/` | Board/host caps (ESP32 audio, first-flash notes) | Open **only** the topic you need; never dump the whole tree |
| — | `third_party/bedside/README.md`, vendored stub `AGENTS.md`/`BEDSIDE.md`, full `eval/` docs | Upstream product / scoring | Almost always — use `bedside doctor|eval|ask|step` instead of loading prose |
| — | Full FAQ / tenets | Strategy | Only when the task is doctrine, not a metal slice |

### Canonical owner (overlap map)

| Topic | Canonical owner | Silico may hold |
|-------|-----------------|-----------------|
| Nine principles, anti-patterns, portable persona | **tig/bedside** `contract/` | One short summary + pin (no kinder soft-fork) |
| Operator gates (`ask` / `step`) | **tig/bedside** surface + CLI | One short pointer here; agent host pickers OK if same contract |
| Day 1 phases, silico verbs, plate, mpy-cross, deploy manifest | **silico AGENTS** + code | Not bedside |
| Operator language (first prompt orient, first-use term defs, big-step why/where) | **silico AGENTS** + [lexicon](specs/lexicon.md) | Not bedside principles; domain on top of contract |
| COM / first-flash (UF2 **or** esptool) / board identity / metal deploy | **silico BEDSIDE.md** + `silico/knowledge/first-flash.md` + CLI | AGENTS Day 1 may point here; avoid full restatement |
| Board/host capability notes (audio, bridges, …) | **silico/knowledge/** (self-improving) | Product must not soft-fork; agents **append** host truths here |
| Eval rubric / fixtures | **tig/bedside** `eval/` | Run CLI; do not paste rubric into context |
| Product domain (idle, vehicle, tunes-as-product, …) | **GCU repo** | Never silico or bedside |

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

### Operator language (silico domain — not a second contract)

These rules sit **on top of** Bedside for this product. They do not soften or replace the nine principles. Phrase book: [specs/lexicon.md](specs/lexicon.md).

#### First prompt orients the operator

The **first operator-facing message** of a Day 1 (or “getting started”) session must help them understand **what they started**, not only what you will do next. Required shape (tone may vary; skeleton may not):

1. **What Silico is** — one or two plain sentences (open host-first spine / “prompt for metal”: agents build and maintain shippable edge products on real boards; Silico is the host tooling and plate, not the product brand).
2. **What a GCU is** — define on first use, then **summarize this GCU** from product truth (`README.md`, `spec.md`, product `AGENTS.md`, workspace markers). Name intent, not codename theater. If product docs are thin, say what is known and what you will clarify after go.
3. **Your role** — you will step them through host setup, plate, proof on the computer, then the board talking over USB.
4. **What you know now** — machine readiness + workspace mode + whether a board is already talking (read-only discovery only).
5. **Where Day 1 is headed** — one short map (host tools → product workspace → plate/host tests → board talk → optional domain loop).
6. **Next mutating step** + **start gate** (structured yes/adjust when available).

Do **not** open with unexplained jargon (“scaffold the plate, pin the spine, green the host gate”) before those words have been defined.

#### Define silico terms on first use

Anytime you use a **silico term** for the **first time in the session**, define it inline in plain language (parenthetical or short clause). After that, keep using the **canonical lexicon name** without redefining — still the full term, not a nickname.

| Term (define on first use) | Operator-facing sense (from lexicon; do not invent softer meanings) |
|----------------------------|----------------------------------------------------------------------|
| **GCU** | General Contact Unit — Silico’s name for one shippable edge product (app + board), not Silico itself |
| **host** | This developer/CI computer (not the board) |
| **plate** | The standard GCU repo template Silico lays down (layout, pin, host tests, HAL/sim stubs) |
| **scaffold** | Running `silico scaffold` / laying that plate into the product checkout |
| **gate** | A named checkpoint: usually the **host gate** (automated tests on the host) or an **operator gate** (yes/no or physical confirm before a scary step) |
| **host gate** | The named host command (typically `pytest -q` / `silico gate`) that must be green before claiming host-done |
| **metal** | The real board / hardware path (confirms; does not alone define done) |
| **product face** | What the operator is supposed to **see or hear** when the product app is running (status LEDs, light pattern, boot sound, etc.) — not a serial version string or a random module GPIO |
| **pin** | Locking Silico (or another package) to a known version in the product’s host deps |
| **deploy** | Writing product files to the board (only after identity + write confirmation) |

If you need a fuller definition, open [specs/lexicon.md](specs/lexicon.md) for that term only — do not dump the whole lexicon into chat.

#### No invented short forms for lexicon terms

Do **not** mint nicknames, abbreviations, or clipped forms for lexicon items in operator-facing prose (or in agent docs you write). Use the **canonical name** from [specs/lexicon.md](specs/lexicon.md).

| Forbidden short form | Use instead |
|----------------------|-------------|
| bare **face** | **product face** |
| “the gate” when ambiguous | **host gate** or **operator gate** (name which) |
| other ad-hoc clips of multi-word terms | full lexicon phrase |

This is bedside manners for silico jargon: inventing “face” for **product face** strands operators the same way unexplained shell does. Product brand names and board part names (e.g. “M5 front panel”) stay ordinary English; do not rebrand them as silico short codes.

**Anti-pattern:** “The GCU will get the plate scaffolded and the host gate will go green” with no definitions.  
**Anti-pattern:** “Confirm the face is alive” (undefined clip of **product face**).  
**Better:** “Your GCU (GCU stands for General Contact Unit — Silico’s term for this shippable edge product) will get a **plate** (the standard project template) via **scaffold**, then we run the **host gate** (automated tests on this computer) until green.”  
**Better:** “Confirm the **product face** (what you should see or hear when the app runs — here, the M5 status LEDs) is alive.”

#### Big steps: why + where in the process

Whenever you prompt the operator for a **big** step (install tools, log into GitHub, create/open the product repo, scaffold/overwrite plate files, plug USB, first-flash, confirm board identity, confirm deploy overwrite, open a metal-proving issue), always include **both**:

1. **Why** — one crisp sentence on what fails or stays blocked without this step.
2. **Where we are** — phase letter/name + one line of done vs next on the Day 1 map (below). Do not assume they track phase letters; restate in plain words.

Keep it short. Do not re-teach the whole playbook every time — only the local map.

**Day 1 map** (use when saying “where we are”):

| Phase | Plain name | Done looks like |
|-------|------------|-----------------|
| 0 | Welcome / start gate | Operator understands Silico + this GCU; clear go |
| A | Machine tools | Git, Python 3.11+, gh, pip ready on this host |
| B | Product workspace | GCU root locked; GitHub identity if needed |
| C | Plate + host gate | Silico pinned; plate scaffolded; `pytest -q` (host gate) green |
| D | Hello metal | Board talks over USB; prepped; confirmed deploy; product face confirmed |
| E | CI proves a metal change | Issue → change → CI green → confirmed flash |
| F | Domain work | Product behavior under test-first / host-first |

Example big-step shape:

> **Where we are:** Day 1 Phase D (hello metal). Host tools, workspace, and the host gate (automated tests on this computer) are done. We still need the board talking over USB before any firmware write.  
> **Why this step:** Without a data USB cable I cannot discover or talk to the board.  
> **Your step:** Plug a data USB cable into the product board.  
> **What I will do next:** Poll for a new serial port, then inspect it with you confirming identity.

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

**Choice walls are contract violations** (Bedside principle 2 / 4), including at phase boundaries. Do **not** end a status message with a free-text numbered menu such as:

> Say when you want to:  
> 1. Review/merge the PR  
> 2. Start domain work from the spec  

That is a multi-choice wall. Use `bedside ask` or the host **structured chooser** (recommended option first). One open free-text question is fine only when the answer is open domain judgment the picker cannot capture — not for “pick next phase fork.”

#### One PR by default (do not PR-spam the operator)

Opening many pull requests as Day 1 proceeds **adds mental burden the operator does not need**: merge order, base-branch graphs, overlapping titles, and “which one is real?” confusion. That is a bedside manners failure (Help the operator / never leave them at a cliff of process).

**Default (unless the operator explicitly asks to stage work as multiple PRs):**

1. Prefer **one open PR** per product session / Day 1 arc (or keep working on `main` with direct pushes if that is already the repo’s workflow and the operator is fine with it).
2. Land progress as **individual, reviewable commits** on that single branch/PR (scaffold → host gate → metal face → domain slice, etc.). Commit history is the staging; the PR list is not.
3. Update the same PR as work continues (push more commits). Do **not** open a second PR for the next phase of the same Day 1.
4. Issues remain fine for tracking intent; **issues ≠ a PR each**.

**Only open multiple PRs when** the operator clearly asks to stage, split review, or stack work (e.g. “separate PRs per issue,” Graphite stack, etc.). Then say in plain language how they relate and merge order — do not invent a multi-PR plan unprompted.

**Anti-pattern:** five open PRs titled variations of “Day 1 scaffold,” “L0 product face,” “L0 domain,” “L1 spine” with no operator request to split. Operator should never have to ask “which order do I merge these?”

#### Announce surprising metal effects (before they happen)

Anything done **to the GCU / board** that may **surprise** the operator — loud or long tones, music, sudden LEDs, motor/actuator motion, first-flash erase, deploy that boots a noisy app, soft-reset that restarts sound — must be **clearly stated in agent output first**.

This is **not** always an extra confirm gate (deploy overwrite already has `confirm-deploy`). It **is** a required **forewarning in plain language** so the human is not startled or left guessing what the device is doing.

**Required before the surprising act** (in the same turn, before the tool/command runs):

1. **What** you are about to do (deploy, soft-reset, first-flash, start app loop, …).
2. **What they may notice** — see/hear/feel (e.g. “the speaker may play a ~15s tone,” “status LEDs will blink,” “board will reboot and reappear on a new COM”).
3. **How long** if non-trivial (seconds, until reset, until stop).
4. **What “done / good” looks like** if relevant (silence after stop, LED pattern ends, version matches).

Do **not** bury this only in code comments, issue text, or a post-hoc “by the way.” Do **not** wait until after the scream.

**Anti-pattern:** `silico deploy … --yes --verify --reset` with no operator-facing line, then a 15-second boot tone with no warning.  
**Better (before deploy/reset):** “I’m about to write firmware to COM7 and soft-reset so the app runs. On this build the product face includes a boot tone for about 15 seconds — you should hear that, then silence when the idle state is reached. Ready; deploying now.”

Irreversible writes still need **operator gate** confirmation. Surprising **effects** need **announcement** even when write permission was already granted earlier in the session (permission ≠ “no heads-up on loud audio”).

Violating Bedside on the operator path violates **Agents operate the host path**.

## Part truth: pointers, not documents

Datasheets are free to download and not free to republish, so silico ships **pointers and parsers, never the documents**. Each GCU carries a `parts.toml`: every part the product is built from, and URLs to where its truth lives (datasheet, SVD, devicetree binding, reference driver, errata).

- `silico parts` validates the file (offline, gate-safe).
- `silico parts --fetch` pulls local grounding copies into `.silico/parts/` (git-ignored, per-checkout, disposable). Ground in those before writing hardware-facing code.
- Prefer machine-readable truth when a part has it: an SVD or DT binding beats a 400-page PDF, and community-patched SVDs carry errata the vendor PDFs do not.
- Never commit fetched documents. The licensing problem evaporates only because the user's own tools fetch the user's own copies.

## Make it better than you found it (non-negotiable)

Anytime the path is rough and you had to **guess, correct, reverse, or research** something that a better doc, plate, script, error message, or small infra fix would have prevented for the **next** agent: do not leave that knowledge only in chat.

1. **Notice friction.** Wrong default port, missing UF2 step, bedside eval miss, Windows-only failure, tool flag that changed: if you stumbled, the next agent will too.
2. **Prefer a durable fix in the right repo.**
   - **Portable operator manners** (contract, surface patterns, CLI init/doctor/eval/ask/step, fixtures, rubric): file and/or fix on **tig/bedside**. Silico is customer 0.
   - **Metal host spine** (ports, deploy, GCU plate, Day 1 playbook specifics): fix in **tig/silico**.
   - **Board/host capability knowledge** (ESP32 audio, first-flash, CDC bridges): extend **`silico/knowledge/`** in the same PR when the truth is reusable (see that tree’s README).
   - **Product domain** (idle control, vehicle, product songs): fix in the **GCU** repo.
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

**One-shot intent:** if the operator already opened the agent **inside the GCU checkout**, stay there. Do not create a second product repo or scaffold into a silico package tree. Silico never encodes a specific product codename; product truth is `spec.md` / product `AGENTS.md` / `README.md`.

### Phase 0 - Welcome the operator (proactive, safe)

Be **proactive in a safe way.** Before the start gate, **do** read-only discovery so your welcome is grounded - do **not** wait for the human to ask whether Git exists. Follow **Operator language** above: orient first, define jargon on first use, never open with an unexplained term soup.

**Allowed before start gate** (read-only / non-destructive):

- Detect OS; run `git --version`, Python version (`py -3` / `python3`), `gh --version`, `pip` check
- `gh auth status` (do not start `gh auth login` until after go, unless they already asked)
- Read product `README` / `spec.md` / workspace layout; run `silico doctor` if installed (**workspace mode** line)
- List serial ports only as information - **do not** inspect/deploy metal or assume a board identity

**Not allowed before start gate:**

- Installing packages, changing PATH, scaffold, deploy, device writes
- Destructive git (reset --hard, force-push) unless the operator already ordered that work
- Walls of shell for the human to paste when you could run the check yourself

Then speak in plain language. Structure (tone may vary; **skeleton may not** — see **First prompt orients the operator**):

1. **What Silico is** (remind them what they started).
2. **GCU defined + this product summarized** from product docs (or honest “thin docs” note).
3. **Role:** you step them through shipping it on this host and then on the board.
4. **What you know now** — machine readiness **and** workspace mode (GCU root vs silico package vs unknown) **and** whether a preferred USB board is already talking.
5. **Where Day 1 is headed** — short map: machine tools → product workspace → plate + host tests → board talk over USB (then domain work). Frame Day 1 as **host plate + device talk**, not host-only.
6. **Next mutating step** in one short sentence (first step after go), with **why** if it is a big step.
7. **Start gate:** ask whether to start or adjust something. Prefer the agent product's **structured question UI** when available (not a multi-option free-text paragraph).

Example shape:

> Welcome. **Silico** is the open host-first spine for building shippable edge products: I (the agent) own setup, tests, and deploy on this computer; you own product judgment and confirm physical or irreversible steps.
>
> You are building a **GCU** (GCU stands for General Contact Unit — Silico’s term for one shippable edge product: app + board). From your product docs, this GCU is: …
>
> I'm here to get it shipped and will step you through it.
>
> On this machine I already checked: Git OK, Python 3.12 OK, gh logged in; workspace mode=gcu (we stay in this product checkout); preferred board not on USB yet (only a demoted adapter).
>
> **Day 1 map:** (A) machine tools → (B) workspace locked → (C) **plate** (standard project template) via **scaffold**, then **host gate** (automated tests on this computer) green → (D) board talks over USB and a confirmed first deploy. We do not stop at host-only.
>
> **Next after go:** install/pin Silico on this host and scaffold/merge the plate here — that gives us the maintainable repo layout and a honest host test path before we touch the board.
>
> Do you want me to start? Or should I adjust something?

Only after a clear **go** (or after applying their adjustments and re-confirming) may you begin **mutating** Phase A work (installs, scaffold, repo create, device paths).

**Anti-pattern:** promising to stop after host gate and "check back before we go near the board." Host gate is a checkpoint, not Day 1 done. After go, you drive through Phase D prep (USB talk + REPL) unless the operator explicitly defers metal.

**Anti-pattern:** first message that only lists tooling status with no Silico explanation and no GCU summary.

### Phase A - Machine prerequisites

When a human must install or approve something, use **Big steps: why + where** (Phase A — machine tools on this host; next is locking the product workspace).

1. Detect OS (Windows / macOS / Linux). Tell them what you detected in one sentence.
2. Ensure **Git** is installed and on PATH. Install if missing; verify with a version command you run.
3. Ensure **Python 3.11+** (`py -3` on Windows, `python3` elsewhere). Install/guide if missing; do not assume `python` means 3. Do not install EOL 3.9/3.10 as the project floor.
4. Ensure **GitHub CLI (`gh`)** is installed. Install if missing; verify `gh --version`.
5. Ensure **pip** works for that same Python.
6. Summarize ready vs needs a human click. Stop cleanly if an installer UI requires them.

### Phase B - Workspace lock (GCU root) and GitHub identity

**Where we are:** Phase B — product workspace (after machine tools). Goal: one clear GCU root; no second invented repo.

**B0 — Lock the product workspace (do this before inventing a repo):**

1. Run `silico doctor` (or detect markers): `spec.md`, `silico.toml`, `firmware/`, product `AGENTS.md`.
2. **`Workspace mode: gcu`** → **cwd is the product root.** Do **not** ask “create a new repo?” Do **not** clone elsewhere. All scaffold/deploy work stays here.
3. **`Workspace mode: silico-package`** → you are inside **tig/silico**. Do **not** scaffold a customer GCU into this tree. Ask the operator to open/create the product checkout, or only work on silico itself if that is the task.
4. **`unknown`** → empty dir or unrelated tree: then Phase B1 (create/clone product).

**B1 — GitHub identity (when a remote product repo is needed):**

1. Check `gh auth status`. If not logged in, walk them through `gh auth login` **one prompt at a time**.
2. If cwd is already a git GCU with `origin`, use it.
3. If create new: confirm a product or codename (**not** `silico`); `gh` create private; clone **or** init in the empty cwd.
4. Remind them: silico stays `github.com/tig/silico`; **their product** is the GCU repo.

### Phase C - Pin silico and scaffold the GCU

**Where we are:** Phase C — pin Silico, **scaffold** the **plate**, green the **host gate**. Next after green: Phase D (board talk), not “done.”

**Do not hand-invent a parallel spine.** Use the package + plate. **Always `silico scaffold .` from the product root** (Phase B0), never from a silico package checkout.

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
2. After the board talks: `silico inspect --port COMx --apply-mpy-pin` — Silico reads device MicroPython **from `sys.implementation`**, maps to an installable pin, and writes **both** `silico.toml` `[runtime].mpy_cross` and `requirements-dev.txt`.
3. Refuse/warn on **ancient** device images; first-flash a current port before applying pins.
4. Packaging: install **`tig-silico`**, never bare `pip install silico`. Prefer tag `v0.1.4+`.
5. `silico doctor` warns on ancient plate pins. Fix before claiming the host compile gate is honest.

2. Scaffold the plate (merge into existing GCU is OK; product `README.md` / `spec.md` are never overwritten):

```text
silico scaffold .
# empty dir also fine: silico scaffold ./my-gcu
# C / ESP-IDF plate (issue #53): silico scaffold . --plate gcu-c
# --force overwrites non-protected plate files only (not README/spec)
```

3. Set product identity in `firmware/version.py` and `silico.toml` from **product files** when present (README title, `spec.md` identity lines); plate defaults are generic only.
4. If `spec.md` exists: host gate proves the **plate + product path** first; domain behavior comes from the **product** spec/AGENTS (not invented in silico). Open host knowledge topics only when the product needs board caps (e.g. `silico/knowledge/esp32-audio.md` for DAC/speaker work).
5. Run host gate until green: `python -m pytest -q` (or `silico doctor` then pytest / `silico gate` / `silico product-path`).
6. Commit and push (or open **one** PR if the repo uses PRs for CI). Further Day 1 work continues as **more commits on the same branch/PR** — see **One PR by default**. Confirm CI/Actions is on.
7. **Do not stop here.** Host gate green is a checkpoint. **Immediately continue into Phase D**.

### Phase D - Talk to real hardware (hello metal)

**Where we are:** Phase D — hello metal. Host plate and host gate are behind you; Day 1 is not done until the board talks, a confirmed deploy runs, and the **operator can see or hear** the product doing something that matches documented “good.”

**Required for Day 1 exit** (not optional polish). Goal: board **talks over USB**, is **prepped** (REPL when that is the runtime), then a **distinct, documented, operator-observable product face** (what the operator sees or hears when the app runs); reconnect is **repeatable**.

Metal COM / first-flash / identity / deploy rules: **[BEDSIDE.md](BEDSIDE.md)** + **[silico/knowledge/first-flash.md](silico/knowledge/first-flash.md)**. USB duplex / lockout: **[silico/knowledge/esp32-usb-serial.md](silico/knowledge/esp32-usb-serial.md)** (open only when needed). Prefer tools: `silico wait-device`, `inspect`, `pull`, `deploy`, `monitor`, and `bedside ask` / `bedside step`. Every physical or overwrite prompt uses **Big steps: why + where**.

#### Phase D0 - Device talks (prep) before any deploy plan

Until true, device is **not** prepped:

1. A real poll shows a candidate (`silico wait-device`, often `--timeout 300`) **or** operator names a port after `silico doctor` (ESP-class CDC may score as preferred; still confirm identity).
2. `silico inspect --port COMx` proves modern REPL **or** you walk **first-flash once** (UF2 **or** esptool — see knowledge/first-flash).
3. Operator confirmed **this port is the product board** (`bedside ask --id confirm-board …` or host UI; default **no** if unsure).
4. Only then: dry deploy → `bedside ask --id confirm-deploy …` → `--yes --verify --reset` → **soft-reset again if the app loop is not running** (verify parks the REPL).

**If the board was missing at Phase 0:** after host gate, ask only for the data cable plug, then **immediately** run a long `wait-device` poll.

**Anti-pattern:** host gate green + "hardware later" with no wait-device/inspect/REPL proof.

##### Serial readiness ladder (before tool-hostile console)

Host gate green ≠ duplex OK. **TX/telem/identity alone is not metal OK.**

1. Stock (or known-good) raw REPL via `silico inspect`.
2. Deploy product **without** `micropython.kbd_intr(-1)` until step 3–4.
3. Prove **round-trip**: host line → device response (not outbound-only spam).
4. Only then: Ctrl-C-is-data + working `repl`/`reboot` door; prove `repl` restores mpremote.
5. Then product face observe (D1).

**Lockout:** door dead / cannot enter raw REPL → **do not thrash redeploy**. Recover **once** (esptool erase+write or UF2), park stock MicroPython, fix duplex on the host, then redeploy. CLI prints the recipe (`LOCKOUT_RECOVERY` / #62).

#### Phase D1 - Operator-observable acceptance (not version-string theater)

Deploy verify + `FW_VERSION` match prove the **host wrote this build**. They do **not** alone prove Day 1 metal.

**Metal is honest only when:**

1. There is a documented **product face** — the **“good”** the operator can **see or hear** without serial folklore (product `spec.md` / `install/`: LEDs, boot riff, status pattern, etc.). Define **product face** on first use if not already defined this session.
2. After soft-reset so the app runs, you **ask the operator** (structured gate or one plain yes/no they answer from the world in front of them) whether that product face is true.
3. If product docs name a product face (e.g. M5 front-panel / side LEDs, speaker riff) and the plate only toggles a generic/dev-board pin (e.g. XIAO GPIO LED that is not the product face): **that is HW confusion, not Day 1 done.** Resolve it with the operator — map pins from product parts/spec/board knowledge, fix `firmware/` / HAL defaults, host-test, redeploy, re-confirm observe. Filing a GitHub issue is a tracker, not acceptance.
4. Product face gaps that block observe are **in-scope Day 1 metal work**. Silico exists to help the operator through this. Do not label the session “on the metal” / “Day 1 complete” while an open issue still says the product face is unproven.

##### GPIO / pin / product face ambiguity → **stop and ask** (mandatory)

When you notice (or should notice) that the **pin, LED, speaker, or product face “good”** in firmware does not clearly match the **product board / spec**, you **must not** quietly assume, monologue an “Honesty” paragraph, or only open a GitHub issue. Never call this bare “face.”

**Required path:**

1. **Stop advancing** Phase E/F claims. Stay in Phase D metal acceptance.
2. **State the mismatch in plain language** (what the code drives vs what the product docs say the product face should look/sound like).
3. **Ask the operator to clarify** with a **structured chooser** (`bedside ask` or host picker) — or one focused free-text question only if the answer is open (e.g. “which LED on the M5 front panel is the product face status light?”). Put the **recommended** guess first when you have one from parts/spec/knowledge.
4. Only after their answer: implement the mapping, host-test, redeploy, then **confirm observe** (“Do you see/hear X?”).
5. Optional: file/update an issue **as a tracker after or while** you are driving the clarify → fix loop — never instead of asking.

Example gate shape (use host picker / `bedside ask`, not a free-text `1/2/3` wall):

```text
bedside ask --id clarify-product-face \
  --prompt "Plate hello blinks GPIO16 (often a small module LED). Product docs want M5 front-panel or side lights as the product face. Which should we treat as Day-1 good on this board?" \
  --choices "m5-front-panel-led,m5-side-led,gpio16-ok-for-now,operator-will-point" \
  --default m5-front-panel-led
```

**Anti-pattern:** agent notices wrong GPIO, writes “Honesty: not the M5 product face LED,” files `#5`, and asks “merge PR or start domain?” without ever asking the operator which light/sound is correct. That **strands** the operator and violates Help the operator / scary surfaces.

**Anti-pattern (forbidden claim):** title or summary like “GCU is on the metal” + an “Honesty” section that admits the product face was **not** proven. That is layered lying: call the layer you proved (`deployed` / `REPL ready`) and leave metal-acceptance open.

**Allowed partial claim (honest):** “Board talks on COM7; deploy verified XUSS 0.0.1; product face LED mapping is unclear — I need you to clarify which light is Day-1 good before we call metal done.” Then run the clarify gate **in that same turn**, not later.

**Phase D steps (order only — details in BEDSIDE + knowledge/first-flash):**

1. Data cable (`bedside step --id plug-usb …` if needed) → long `silico wait-device`.
2. `silico doctor` / `silico inspect --port COMx` → confirm-board gate.
3. No modern REPL → **first-flash once**:
   - RP2040-class: UF2 (BOOT+RESET → `RPI-RP2`).
   - ESP32-class: esptool erase + `ESP32_GENERIC` (or board variant) at `0x1000` (see knowledge/first-flash).
   - Re-inspect until talk; then `--apply-mpy-pin` only on non-ancient MP.
4. Optional backup: `silico pull <dir> --port COMx`.
5. Dry plan: `silico deploy --port COMx` → confirm-deploy → **announce surprising product face effects** (tones, long audio, bright LEDs, motion — see **Announce surprising metal effects**) → `silico deploy --port COMx --yes --verify --reset`.
6. Soft-reset so **main.py runs as the app** (deploy verify uses REPL and parks the loop). If the soft-reset itself will start sound/motion, announce that **before** the reset. If raw REPL fails: product `repl` door or boot window (Ctrl-C may be data).
7. **Operator-observable check:** document the **product face** “good”; confirm with the operator from the bench. If product face ≠ plate generic pin (or mapping is unclear): **clarify with the operator first** (structured ask), then fix, redeploy, re-confirm observe — do not stop at version match or issue-only.
8. Optional: `silico monitor --port COMx --duration 10`.
9. Document `install/` leave-behind (Day-2 one-liner + product face “good”: LEDs/audio/etc.).

Non-Python deploy assets (e.g. audio riffs) may appear in `[deploy].core`; host hygiene skips them as copy-only.

### Phase E - CI proves metal change

1. Ask the human to open a GitHub Issue on the **GCU** repo (or create with `gh` after approve). Title example: `Change the firmware blink pattern (distinct A vs B)`.
2. Implement: firmware behavior change **and** host tests/CI green. Domain follows product `spec.md` when present.
3. Push commits to the **existing** Day 1 branch/PR (or open the first PR if none yet). Do **not** open a new PR per phase. Watch CI; fix red builds.
4. Deploy only after operator confirmation again if overwriting; confirm the visible/audible acceptance matches the issue.
5. Close the issue with a short note linking the commit/PR.

Closed loop: **issue → agent → host gate → CI → metal**.

### Phase F - Domain work (still Day 1)

1. Human points at domain intent (docs, notes, rough brief). You do **not** invent the vertical moat.
2. Write detailed specs, tests, and `firmware/` under test-first and host-first rules.
3. Staged plan as **cross-linked, tagged GitHub Issues** for proprietary work — **issues stage work, not a PR per issue** unless the operator asked for multi-PR staging.
4. Host gate green locally before claiming done. Flash only confirms.
5. Push more commits to the same branch/PR; CI matches local. Change requests arrive as GitHub Issues. Implement them without requiring the human to know git branches unless they want to.

#### Spec gaps

While coding, you will find product `spec.md` items that are lacking, confusing, or wrong.

**Split by whether the gap blocks operator-observable metal:**

| Gap type | Rule |
|----------|------|
| **Blocks see/hear acceptance** (which LED is the product face, pin map for this board, boot riff, “what good looks like”) | **In-scope now.** **Ask the operator to clarify** (structured gate) as soon as you notice the mismatch — do not only monologue or file an issue. Then parts.toml / knowledge / board docs / implement + confirm. Spec rewrite can still wait, but **bench truth cannot**. |
| **Domain polish / later product depth** (full protocol, vehicle appendix, extra modes) | Do not block the current host-green slice. Note the gap; **late step** offer a proposed `spec.md` edit after host gate is green or at a phase boundary. |

For non-blocking gaps:

1. Prefer configurable defaults, explicit assumptions in code/issue comments, and host tests.
2. Quietly note gaps (issue comment or checklist).
3. **Late step** — prompt the operator: what was wrong/missing, a proposed edit, and ask (structured chooser) whether to update the spec **now**.
4. Edit the product spec only after a clear **yes**.

### Day 1 exit criteria (before Day 2)

Metal bar detail: [BEDSIDE.md](BEDSIDE.md). Spine/DoD: layered table below.

- [ ] **Device talks over USB** (`silico inspect` / REPL) and was **prepped** (runtime once if needed).
- [ ] **Operator-observable metal:** after confirmed deploy + app running, the operator can **see or hear** the documented **product face** for **this** product (not only a plate pin that is not the product face). Agent worked through HW confusion; did not stop at version match + issue filed.
- [ ] Host gate green locally and on GitHub.
- [ ] Device `FW_VERSION` matches host.
- [ ] One documented update path (BEDSIDE Day-2 leave-behind) that states what good looks/sounds like.
- [ ] Silico pinned as host dependency.
- [ ] Operator helped through first flash/serial without assumed ops expertise.
- [ ] Any “what next?” phase fork used a **structured chooser**, not a free-text numbered menu.

**Not exit criteria:** host gate alone; scaffold alone; deploy verify / version match alone; deferred metal with no poll/inspect; “honesty” note that the product face is unproven while the title says on-the-metal; issue filed instead of resolving observe.

**Day 2:** same update path; unit to potential customer or field trial.

## Definition of done (layered)

Host-first is **not** host-only. Claims must name the layer they prove:

| Layer | Claim example | Required proof |
|-------|---------------|----------------|
| **Host** | Domain logic / sim / plate | Named host gate green (default: `pytest -q`). CI green if remote exists. |
| **Metal I/O** | Sensing or actuation on pins | Inject/measure on **named** pins (or harness signature), not only LED blink or version import. |
| **Vehicle / field** | Product acceptance on real plant | Product Appendix / field procedure; not bench buzz alone. |
| **Deployed** | Board runs this build | Device `FW_VERSION` matches host after confirmed write; optional harness OK. **Not** the same as product metal acceptance. |
| **Metal accepted (Day 1)** | Product on the bench | Operator **sees or hears** documented **product face** for this GCU; pin / product face confusion resolved or explicitly deferred as **not Day 1 complete**. |
| **Issue fixed** | Ticket closed | Proof matching the issue's **stated layer**. CI green alone is not enough for a metal/vehicle claim. |

### HAL seam (Silico-owned pattern)

The host gate is only honest if domain firmware is host-importable and hardware stays behind a seam:

1. **Contract** (`firmware/hal.py`) — method surface; no `machine`.
2. **Device backend** (`firmware/hal_board.py` or product equivalent) — only modules listed in `silico.toml` `[hal].allow_machine` may import `machine`.
3. **Host double** (`sim/hal_double.py`) — same method names for pytest.
4. **main** — `init(hal=…)` / `tick`; no top-level hardware; boot only as `__main__`.

Enforce with `silico gate` (deploy-set CPython import + machine allowlist). Do not re-derive a private HAL shape per GCU when the plate already ships one.

### C / ESP-IDF backend (`language = c`)

Opt-in plate: `silico scaffold . --plate gcu-c`. Runtime from `silico.toml` (`language = c`, `toolchain = esp-idf`, `chip`, `[deploy].mode = idf-flash`).

| Verb | C behavior |
|------|------------|
| `gate` | Device-header allowlist (`#include`) + `[host].gate` (cmake/ctest) when `build/host` exists |
| `product-path` | Host C tests must use shipped defaults table (compiled use) |
| `inspect` | Serial identity line; no mpremote; no `--apply-mpy-pin` |
| `deploy` | `idf.py build` + flash; plan says full image overwrite; `--prune` / `--verify-import` refuse |

Default plate stays MicroPython. Arduino is not this path (see issue #59). First consumer for C Day 1 is **tig/xuss-c** (spec-first product; not closed by hello-metal alone).

### Forbidden closes

- Do **not** close a **P0 sensing/actuation** issue as done with only host/sim code if the device path is still a stub (`pass`, empty IRQ, no feed into the estimator). Either:
  1. land metal code that proves the pin path, or
  2. leave a **blocking metal follow-up** open (title/status makes metal-TODO obvious) and do not narrate the product as metal-ready.
- Do **not** mark vehicle/Appendix acceptance done without the vehicle procedure (or explicit defer with open tracker).
- Do **not** mark Day 1 / “on the metal” done when the operator cannot see or hear the **product face**, even if deploy verify and version match passed. Filing “product face LED wrong pin” and moving to Phase F is a forbidden close.
- Do **not** notice GPIO / product face mismatch and skip asking the operator to clarify (honesty note or issue alone is not a clarify gate).
- Do **not** invent short forms of lexicon terms (e.g. bare “face” for **product face**) in operator-facing prose.
- Do **not** present phase forks as free-text `1. / 2. / 3.` menus in chat when a structured chooser exists (or `bedside ask` is available).
- Do **not** open a fan-out of PRs for sequential Day 1 / same-session work unless the operator asked to stage multi-PR. One PR + individual commits is the default.
- Do **not** deploy, soft-reset, or otherwise drive metal that may play loud/long audio, flash bright patterns, or move actuators without a clear operator-facing forewarning of what will happen and for how long.
- Do **not** claim metal serial OK from identity/telem TX alone, or enable `kbd_intr(-1)` before round-trip + working `repl` re-entry (see serial readiness ladder; #62).
- Do **not** thrash full-erase/redeploy when the console is locked; recover once, park stock MP, stop.
- Prefer issue titles like `host-done / metal-TODO` when splitting layers is honest — and **never** put “on the metal” in the same message as metal-TODO.

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
7. Do not open many PRs for one Day 1 arc unless the operator asked to stage multi-PR (one PR, many commits).
8. Do not surprise the operator with metal effects (loud/long tones, motion, sudden reboot loops) without clearly announcing what will happen first.
9. Do not deploy host `sim/` or silico package modules to the board.
10. Do not claim external adoption or platform status without scoreboard evidence.
11. Do not rewrite PR titles, Grady quotes, or Tig quotes unless the human asks.
12. Do not start Arduino / multi-runtime work unless a GCU forces it (v2).
13. Do not burn an hour recovering from silico friction and leave no issue or doc fix for the next agent.

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
