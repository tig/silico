# AGENTS.md

Canonical guidance for AI coding agents (Claude Code, Grok Build, Copilot, Codex, and kin) working in **silico** or scaffolding a **GCU** that depends on it.

Human overview: [README.md](README.md). Tenets: [specs/tenets.md](specs/tenets.md). Phrase book: [specs/lexicon.md](specs/lexicon.md). first-ship narrative: [specs/prfaq.md](specs/prfaq.md) FAQ 5. Build target: [specs/silicov1.md](specs/silicov1.md).

## FIRST ACTION — Stage 0 (first ship / “getting started for agents”)

When the human points at silico / first ship / “getting started for agents”, do **this exact order**.

### 0 — Load this file (full text, not a fetch digest)

**You are not following silico until you have the full text of this `AGENTS.md`** (local silico clone, GCU plate after scaffold, or download `https://raw.githubusercontent.com/tig/silico/main/AGENTS.md` and **read the file**).

| Fail | Correct |
|------|---------|
| WebFetch `github.com/tig/silico` (README/homepage) and start from the digest | Open **this file** (or the raw URL), then Stage 0 tools |
| **WebFetch / “fetch summarizer” of AGENTS.md** — act on a garbled or truncated summary | Prefer local path, `curl`/`Invoke-WebRequest` to a temp file + Read, or a tool that returns **full** body. If a summarizer garbled it: **re-download and read full text before any Stage 0 claim** |
| Treat a README one-liner about Stage 0 as the full contract | README is human entry; **this file is Priority 1** for agents |

A second-hand README or **lossy fetch summary** is luck, not diligence — even if it mentions `silico welcome`.

### 1 — Stage 0 tools (after this file is open in full)

**Do not** open with tooling narration, COM folklore, PR strategy, `bedside init`, vendoring `third_party/`, scaffold, or a start-gate chooser.

```text
# --- TURN 1 (0a only): run tool, paste orientation, name the human act, END TURN ---
silico welcome
# Paste/adapt that output as the ONLY operator-facing content of this turn.
# End with the operator next-step line from welcome (reply ok/go when ready).
# Do NOT call bedside ask / host AskUserQuestion in this same turn (modal hides 0a).
# Do NOT leave a free-text cliff ("Start gate is next") with no human act named.

# --- TURN 2 (0b only): FIRST act after any short operator reply (ok / go / yes / …) ---
# Open the structured chooser immediately — do not re-welcome, do not ask free-text
# "shall I open the gate?", do not wait for a second free-text "yes".
bedside ask --id start-first-ship --prompt "Start first ship on this machine?" --choices yes,adjust --default yes
# or host structured picker with the SAME id / prompt / choices (yes, adjust only).
# Say once if using the host gate shell.
```

| Rule | Detail |
|------|--------|
| **Load full AGENTS first** | README/homepage alone fails. **Fetch digests of this file fail.** Full text or re-download. |
| **Two turns: 0a then 0b** | **Hard rule.** Orientation is turn 1. Start gate is the **first** act of turn 2. Same-turn “welcome then picker” fails when the host UI steals focus. |
| **0a ends with a human act** | Operator-facing close must say what to do next (e.g. reply `ok` / `go`). Never leave only “Start gate is next” at a free-text prompt with no chooser and no next step. |
| **Turn 2 = chooser first** | After any short reply, open the **structured** start gate immediately. Free-text-only turn 2 fails Stage 0b (Bedside: never leave them at a cliff; no free-text choice wall). |
| **0a is a completed chat message** | Tool log only fails 0a. 0a must be a finished assistant message the operator can scroll to **without** a modal open. |
| **Welcome is the skeleton** | Do not hand-build a multi-section status report instead of `silico welcome`. |
| **Gate prompt is short** | Title/prompt = one question. **No** Stage A–D monologue in the chooser. Optional: “Orientation is in the message above.” |
| **Choices only `yes` / `adjust`** | Do **not** invent `Go`, `Host-only`, `Look around`. Host-only is a named anti-pattern unless the operator **adjusts** after a short re-gate. |
| **No mutate before go** | Before **yes** on start-first-ship: no `bedside init`, vendor, scaffold, commit/push, product-tree installs. |
| **Doctor fail ≠ skip 0a** | Missing GCU `bedside.toml` is normal. Still show 0a; fix pin after go via plate. |
| **Host picker OK** | Same id/prompt/choices; say once. Still **turn 2 only**. Decline / exit 10 = halt writes. |

**Harness note (Claude Code / similar):** Host structured questions take focus immediately → **split turns**. After 0a, the session **must** resume into a **chooser**, not a bare free-text prompt. If the operator only saw free text after orientation, you failed 0b — open the start-gate picker on the next opportunity without redoing a long 0a.

After **go**: Stage A tools → B workspace → C plate + host gate → D metal. Full stages and metal rules are below.

---

## Agent context load path (read once)

Context is finite. **Do not** open every manners file into the active window.

| Priority | Open | Job | Skip when |
|----------|------|-----|-----------|
| 1 | This file (`AGENTS.md`) | Silico spine: first-ship stages, silico CLI, plate, host/metal DoD | — |
| 2 | `bedside.toml` + contract path it names | Normative portable manners (nine principles) | Already summarized below and you are not changing manners |
| 3 | `BEDSIDE.md` | **Metal domain pack only** (COM, first-flash, deploy identity) | Already in first-ship metal sections of this file for the current step |
| 4 | One topic under `silico/knowledge/` | Board/host caps (ESP32 audio, first-flash notes) | Open **only** the topic you need; never dump the whole tree |
| — | `third_party/bedside/README.md`, vendored stub `AGENTS.md`/`BEDSIDE.md`, full `eval/` docs | Upstream product / scoring | Almost always — use `bedside doctor|eval|ask|step` instead of loading prose |
| — | Full FAQ / tenets | Strategy | Only when the task is doctrine, not a metal slice |

### Canonical owner (overlap map)

| Topic | Canonical owner | Silico may hold |
|-------|-----------------|-----------------|
| Nine principles, anti-patterns, portable persona | **tig/bedside** `contract/` | One short summary + pin (no kinder soft-fork) |
| Operator gates (`ask` / `step`) | **tig/bedside** surface + CLI | One short pointer here; agent host pickers OK if same contract |
| first-ship stages, silico verbs, plate, mpy-cross, deploy manifest | **silico AGENTS** + code | Not bedside |
| Operator language (first prompt orient, first-use term defs, big-step why/where) | **silico AGENTS** + [lexicon](specs/lexicon.md) | Not bedside principles; domain on top of contract |
| COM / first-flash (UF2 **or** esptool) / board identity / metal deploy | **silico BEDSIDE.md** + `silico/knowledge/first-flash.md` + CLI | AGENTS first-ship metal sections may point here; avoid full restatement |
| GCU `bedside.toml` pin (sibling paths to silico vendor) | **plate** ships it; GCU keeps it | Do not leave GCU without a pin and then invent a prose path |
| Board/host capability notes (audio, bridges, …) | **silico/knowledge/** (self-improving) | Product must not soft-fork; agents **append** host truths here |
| Eval rubric / fixtures | **tig/bedside** `eval/` | Run CLI; do not paste rubric into context |
| Product domain (idle, vehicle, tunes-as-product, …) | **GCU repo** | Never silico or bedside |

### Context budget rule

Prefer **tools that encode manners** (`silico welcome|doctor|wait-device|inspect|deploy`, `bedside doctor|eval|ask|step`) over re-loading essays. If two files say the same rule, follow the **canonical owner** and treat the other as a pointer.

**Stage packs (token lever, #79):** do not paste the entire `AGENTS.md` into every turn. Keep Stage 0 + hard rules (manners tools required, decline = halt) as the session core; load one stage on demand:

```text
silico agents --stage list
silico agents --stage core    # manners tools hard rules
silico agents --stage d       # hello metal only
silico agents --stage lang-c  # C / ESP-IDF backend
```

Same file is the only source of truth — packs are extracts, not a soft-fork.

### Manners tools are the operator path (required, not optional)

**Hard rule:** On first ship (and any operator-facing metal/host path), the manners tools **are** the path. They are not optional flavor on top of a self-driven install script.

| Required tool / gate | When | Failure if skipped |
|----------------------|------|--------------------|
| `silico welcome` | Stage **0a** source of orientation (**first**) | Hand-built long status dump / discovery theater instead of the skeleton |
| `bedside ask` or host picker (**same contract**) | Stage **0b** start gate; board identity; deploy overwrite; stage forks | Free-text walls; monologue past the human; essay stuffed into the chooser |
| `bedside step` or host step (**same contract**) | Plug USB, BOOT/RESET, OS dialogs | Multi-step essays; leaving them at a cliff |
| `bedside doctor` | Before **metal/write** gates that need the pin; **not** a blocker for 0a | Pre-go `bedside init` / full vendor into GCU so doctor is green before welcome |
| `silico doctor` / `wait-device` / `inspect` / `deploy` | Stages A–D as named | Blind serial; deploy without identity |

**Not a substitute for the path:**

- Long chat status reports, PR strategy monologues, or COM folklore tables **before** or **instead of** the welcome skeleton and start gate.
- “I ran discovery myself, so I can skip `silico welcome`.”
- “`bedside doctor` failed, so I must `bedside init` / vendor before orientation.” **Wrong.** Show 0a first; fix pin after go (plate ships `bedside.toml`).
- “Host `AskUserQuestion` means I never need `bedside`.” Host pickers are **same contract, alternate shell** — still one short gate, recommended first, exit on decline. Prefer `bedside ask|step` when the CLI can reach the operator.
- “Prefer doing over instructing” does **not** mean drive past operator gates, commit/push while a gate is open or declined, or treat first ship as an unattended install script. Doing the host work is correct; **doing past the operator’s yes/no is not.**

## What silico is

**Prompt to metal.** Open host-first spine for vertical edge products (GCUs). Not a company product line. Not the vertical domain app.

We work backwards from:

> With just Claude Code on my Mac and my hardware spec, I had the device working end-to-end in a few hours, and in a field test the day after that. Silico is now a foundational piece of our company's technology.

If a change does not make that sentence more true, it is not v1 work.

## Tenets (summary)

Full text: [specs/tenets.md](specs/tenets.md) (unless you know better ones).

1. **Software is not the moat.**
2. **Agents write the code.**
3. **Agents operate the host path.**
4. **Make it better than you found it** (also **compound** — [lexicon](specs/lexicon.md#compound)).
5. **Edge that just works is hard.**
6. **Vertical teams are the customer.**
7. **Prompt to metal.**
8. **Default is a product choice, not a quality ranking.**
9. **Host first.**
10. **Apps stay apps.**
11. **Extract, then open.**

## Help the operator (Bedside)

We follow **[Bedside](https://github.com/tig/bedside)**. Load rules per **Agent context load path** above — do not also dump the full vendored README into context.

- Pin / paths: [bedside.toml](bedside.toml)
- Contract (normative): [third_party/bedside/contract](third_party/bedside/contract)
- Metal domain notes only: [BEDSIDE.md](BEDSIDE.md)
- Vendor stamp: [third_party/bedside/VENDOR.md](third_party/bedside/VENDOR.md)

Summary (full contract is normative; do not soft-fork):

1. Assume low ops literacy, high judgment.
2. No wall of unexplained shell.
3. Prefer doing over instructing — **run checks and installs yourself; do not paste command walls.** This is **not** a license to mutate, commit, push, scaffold, or flash past an open or declined operator gate.
4. Human acts: explicit, one step, dumb-simple.
5. Own first-time setup from zero.
6. Own scary surfaces in plain language.
7. Confirm in their words before irreversible or physical steps.
8. Never leave them at a cliff.
9. Teach only what the update path requires.

Silico domain (metal / host path) details: **BEDSIDE.md** and first-ship stages below. Host tools that encode manners: `silico welcome`, `silico doctor`, `wait-device`, `inspect`, `deploy --yes`, plus Bedside operator gates below.

Prove manners: `bedside doctor` and `bedside eval` (vendored fixtures include `operator-gate-ask` / `operator-gate-step`). On **first ship Stage 0**, a missing GCU pin does **not** block `silico welcome` / 0a. Fix the pin **after go** (plate ships `bedside.toml` → sibling silico vendor; or `pip install -e` the CLI). Do **not** pre-go `bedside init` / full vendor so doctor is green before orientation.

### Operator language (silico domain — not a second contract)

These rules sit **on top of** Bedside for this product. They do not soften or replace the nine principles. Phrase book: [specs/lexicon.md](specs/lexicon.md).

#### First prompt orients the operator

The **first operator-facing message** of a **first-ship** (getting-started) session must help them understand **what they started**, not only the next action. Required shape (tone may vary; skeleton may not):

1. **What Silico is** — one or two plain sentences (open host-first spine / “prompt to metal”: agents build and maintain shippable edge products on real boards; Silico is the host tooling and plate, not the product brand).
2. **What a GCU is** — define on first use, then **summarize this GCU** from product truth (`README.md`, `spec.md`, product `AGENTS.md`, workspace markers). Name intent, not codename theater. If product docs are thin **or contradictory**, say so and plan **spec interview mode** after go (see that section) — do not invent domain moat to fill the holes.
3. **Role** — step them through host setup, plate, proof on the computer, then the board talking over USB.
4. **What you know now** — machine readiness + workspace mode + whether a board is already talking (read-only discovery only).
5. **Where first ship is headed** — one short map (host tools → product workspace → plate/host tests → board talk → optional domain loop). Say **first ship**, not “Day 1.”
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
| **first ship** | The getting-started path: cold start → operator-observable product face on metal (not a calendar “day”) |
| **stage** | One ordered chunk of the first-ship path (0 welcome, A tools, B workspace, C plate, D metal, …) |
| **gate** | A named checkpoint: usually the **host gate** (automated tests on the host) or an **operator gate** (yes/no or physical confirm before a scary step) |
| **host gate** | The named host command (typically `pytest -q` / `silico gate`) that must be green before claiming host-done |
| **metal** | The real board / hardware path (confirms; does not alone define done) |
| **product face** | What the operator is supposed to **see or hear** when the product app is running (status LEDs, light pattern, boot sound, etc.) — not a serial version string or a random module GPIO |
| **pin** | Locking Silico (or another package) to a known version in the product’s host deps |
| **deploy** | Writing product files to the board (only after identity + write confirmation) |
| **compound** | Make it better than you found it: turn friction into a durable fix/issue so the next agent is faster (not chat-only recovery) |

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
**Better:** “This GCU (GCU stands for General Contact Unit — Silico’s term for this shippable edge product) gets a **plate** (the standard project template) via **scaffold**, then we run the **host gate** (automated tests on this computer) until green.”  
**Better:** “Confirm the **product face** (what to see or hear when the app runs — here, the M5 status LEDs) is alive.”

#### Big steps: why + where in the process

Whenever you prompt the operator for a **big** step (install tools, log into GitHub, create/open the product repo, scaffold/overwrite plate files, plug USB, first-flash, confirm board identity, confirm deploy overwrite, open a metal-proving issue), always include **both**:

1. **Why** — one crisp sentence on what fails or stays blocked without this step.
2. **Where we are** — stage letter/name + one line of done vs next on the first-ship map (below). Do not assume they track stage letters; restate in plain words.

Keep it short. Do not re-teach the whole playbook every time — only the local map.

**First-ship map** (use when saying “where we are”):

| Stage | Plain name | Done looks like |
|-------|------------|-----------------|
| 0 | Welcome / start gate | Operator understands Silico + this GCU; clear go |
| A | Machine tools | Git, Python 3.11+, gh, pip ready on this host |
| B | Product workspace | GCU root locked; GitHub identity if needed |
| C | Plate + host gate | Silico pinned; plate scaffolded; `pytest -q` (host gate) green |
| D | Hello metal | Board talks over USB; prepped; confirmed deploy; product face confirmed |
| E | CI proves a metal change | Issue → change → CI green → confirmed flash |
| F | Domain work | Product behavior under test-first / host-first |

Example big-step shape:

> **Where we are:** first ship, Stage D (hello metal). Host tools, workspace, and the host gate (automated tests on this computer) are done. We still need the board talking over USB before any firmware write.  
> **Why this step:** Without a data USB cable I cannot discover or talk to the board.  
> **Your step:** Plug a data USB cable into the product board.  
> **Next:** Poll for a new serial port, then inspect it with the operator confirming identity.

### Operator gates: `bedside ask` / `bedside step` (not multi-choice free text)

Do **not** restate long "how to ask the human" essays. **Use the gate tools** (required path — see **Manners tools are the operator path**):

| Gate | Tool | Example |
|------|------|---------|
| Structured choice / yes-no | `bedside ask` | start first ship, confirm board identity, confirm deploy overwrite |
| One physical / browser act | `bedside step` | plug data cable, hold BOOT, approve OS dialog |

```text
bedside ask --id start-first-ship --prompt "Start first ship on this machine?" --choices yes,adjust --default yes
bedside ask --id confirm-board --prompt "Is COM9 the product board for this session?" --choices yes,no --default no
bedside ask --id confirm-deploy --prompt "Overwrite device firmware on COM9 now?" --choices yes,no --default no
bedside step --id plug-usb --prompt "Plug a data USB cable into the board." --expect "Board power LED on or new COM in wait-device."
```

Exit codes (agents): **0** recommended path / step confirmed; **10** declined, other choice, or human still needed; **30** setup error.

#### Gate prompt shape (short — no essay inside the chooser)

The **why + where** map belongs in the **chat turn before** the gate (Big steps), not stuffed into `--prompt` / the picker body.

| OK in the gate | Not OK in the gate |
|----------------|--------------------|
| One clear question | “Where we are… Why… Inspect found… Next we will…” walls |
| Recommended choice first | Multi-paragraph status + the chooser at the bottom |
| Default that matches bedside (e.g. confirm-board default **no**) | Hiding the scary act inside a long monologue |

#### Decline / exit 10 = halt writes (hard rule)

When the operator **declines**, picks **adjust** / non-recommended, or the gate returns **exit 10** (or the host picker equivalent):

1. **Stop mutating** for that gated act: no further scaffold overwrite, commit, push, deploy, first-flash, or “full first-ship status” monologue as if you were still green.
2. **One short reply:** acknowledge the decline in plain language; offer **one** next gate (adjust path) **or** stop cleanly. Do not invent “continue with best judgment” past a no.
3. **Do not** commit + push + open PR + summarize the whole first-ship map while a board/start/deploy gate is declined or still open.
4. Host product nudges (“continue with best judgment”) **never** override an explicit operator **no** on a bedside-shaped gate.

Nothing in this file licenses: *system said declined → I still committed, pushed, and monologued.*

#### Host structured UI (same contract, not a second path)

**Also OK:** the agent product's **structured question UI** (pickers, `AskUserQuestion`, etc.) **only when** it implements the **same contract**: one gate, recommended first, short prompt, no multi-option free-text walls, and **decline = halt** as above. Free text remains for open domain judgment only.

| Correct read | Wrong read |
|--------------|------------|
| Host picker ≈ `bedside ask` shell | “Host UI means I skip Bedside forever” |
| Prefer `bedside ask|step` when CLI works | Note `bedside doctor` fail and never init |
| Same ids/intent (`start-first-ship`, `confirm-board`, …) | Long chat chooser that re-asks the playbook |
| Host picker when agent stdin cannot reach the operator | Silent substitution with no mention; free-text multi-choice wall |

**Harness note:** many agent hosts cannot forward a TTY to `bedside ask` stdin. In that case the host structured picker is the **sanctioned** gate shell (same ids/contract). Prefer CLI when it works; when it cannot, use the picker and state once that you are using the host gate shell. Do **not** treat a missing TTY as license to skip gates or monologue past the operator.

Non-interactive / CI: `--answer` on `ask`, `--confirm` / `--decline` / `--no-wait` on `step` (see `bedside ask --help`).

**Choice walls are contract violations** (Bedside principle 2 / 4), including at stage boundaries. Do **not** end a status message with a free-text numbered menu such as:

> Say when you want to:  
> 1. Review/merge the PR  
> 2. Start domain work from the spec  

That is a multi-choice wall. Use `bedside ask` or the host **structured chooser** (recommended option first). One open free-text question is fine only when the answer is open domain judgment the picker cannot capture — not for “pick next stage fork.”

#### Repo workflow: inspect, then choose main vs PRs

Before the first push of first ship (or when locking the product workspace), **inspect the GCU remote** — do not assume a PR workflow.

**Lightweight signals** (use `gh`; a few checks, not a research project):

| Signal | How (examples) |
|--------|----------------|
| Branches | `gh api repos/{owner}/{repo}/branches --jq 'length'` (or list names) |
| Open / recent PRs | `gh pr list --limit 5`; `gh pr list --state all --limit 10` |
| Issues | `gh issue list --limit 5`; issue count / activity |
| Default branch protection / required checks | only if already visible; do not dig for policy theater |

##### Maintainer practice GCUs: always `main` (hard override)

These remotes are **first-ship / harness practice trees**, not product teams with a merge queue. **Always use the direct-to-`main` strategy** — even if `gh pr list` shows past PR history (prior harness runs leave noise).

| Remote | Role |
|--------|------|
| [tig/xuss](https://github.com/tig/xuss) | MicroPython demo GCU |
| [tig/xuss-c](https://github.com/tig/xuss-c) | C / ESP-IDF demo GCU |
| [tig/xuss-lame](https://github.com/tig/xuss-lame) | Thin/messy interview practice GCU |

**Do not** open a “repo workflow” chooser offering `pr` vs `main` for these three. **Do not** invent a PR path because “this repo has recent PR history.” Land first ship as **individual commits on `main`** (watch CI on push).

**Clean start point (before mutating Stage A–C):** for the practice GCU you are shipping, verify **`origin`’s default branch tip is the product-only clean start**, not a mid-flight scaffold from a previous agent.

| Check | How |
|-------|-----|
| Tip message | `gh api repos/tig/<repo>/commits/main --jq .commit.message` (or `git log -1 origin/main`) |
| Clean start looks like | Subject contains **`product-only clean start`** (e.g. `chore: product-only clean start (no silico agent guidance)`) — thin product docs only, no plate/`firmware` first-ship residue from a prior run |
| Local matches remote | `git fetch origin` then `git status -sb` / `git rev-parse HEAD origin/main` — do not build on a dirty or divergent checkout without operator go |

If tip is **not** clean start (e.g. prior “Scaffold plate…”, half-done first ship on `main`):

1. **Stop** committing more first-ship work as if this were a fresh path.
2. Tell the operator in plain language: remote is past clean start; options are **reset to clean start** (only with explicit operator go — destructive) or **continue this tree** as an update path.
3. Do **not** silently open a PR “to keep main clean” as a substitute for checking clean start.

When the operator’s goal is a **fresh first-ship harness run**, all three practice remotes they care about should be at clean start **before** go (at least the one cwd targets; if they named the whole Xuss family, check each).

**Anti-pattern:** Stage C green → “repo has PR history → recommend `pr`” on `tig/xuss-c` (or xuss / xuss-lame). That is the failure this override exists to prevent.

**Simple repo** (typical early GCU / first-ship practice tree — **and always the three practice GCUs above**): few or no extra branches, little or no PR history, thin issue tracker.

1. **Recommend committing and pushing straight to `main`** (or the default branch). For **xuss / xuss-c / xuss-lame**, this is **required**, not optional.
2. Say in plain language: PRs can wait until the product is more active; direct-to-main keeps CI on every push without merge-queue overhead.
3. Use a **structured chooser** if they might prefer PRs anyway; recommended option first: **commit to main**. **Skip the chooser** for the three practice GCUs (already decided: main).
4. Land first ship as **individual, reviewable commits** on that branch. Issues stage intent; **issues ≠ a PR each**.

**Well-used repo** (active branches, open or recent PRs, non-trivial issue history, or operator already works via PR) — **does not apply** to tig/xuss, tig/xuss-c, tig/xuss-lame (see override above):

1. **Do not silently force direct-to-main.**
2. **Verify with the operator** (structured chooser) whether changes should go through **PRs** or **direct commits to the default branch**.
3. **If they choose PRs, say explicitly:** CI/CD proof becomes an **extra step** — open/update the PR, wait for Actions (or equivalent) green, then merge. Host gate green locally is not the same as merge-path green until that loop runs.
4. Prefer **one open PR** per product session / first-ship path — not a PR per stage. Land progress as commits on that single PR. Do **not** open a second PR for the next stage of the same first ship unless they asked to stage multi-PR.

**Only open multiple PRs when** the operator clearly asks to stage, split review, or stack work (e.g. “separate PRs per issue,” Graphite stack). Then say how they relate and merge order — do not invent a multi-PR plan unprompted.

**Anti-pattern:** invent a PR workflow on a quiet repo that only needed `main` commits.  
**Anti-pattern:** invent a PR workflow on **tig/xuss**, **tig/xuss-c**, or **tig/xuss-lame** because of leftover harness PR history.  
**Anti-pattern:** five open PRs titled variations of “first ship scaffold,” “L0 product face,” … with no operator request to split.  
**Anti-pattern:** choose PRs and never watch CI — that skips the reason PRs exist for that team.  
**Anti-pattern:** first-ship mutate on a practice GCU whose `origin/main` tip is not the product-only clean start, without telling the operator.  
**Anti-pattern:** tip is clean start (docs only) but the agent cherry-picks or replays a previous attempt’s display/audio/UI firmware from older commits / other branches / “last session worked” — that is **past-HEAD salvage** (see **Product truth is HEAD**). Verboten.

### Product truth is HEAD (no past-HEAD salvage)

**Hard rule (first ship, clean start, abort-and-retry SOP — all GCUs, not only practice trees):**  
Implement product domain and **product face** from **this checkout at current HEAD** (plus uncommitted work from **this** session), the **operator**, and the **silico spine** (plate, board profiles, knowledge, parts pointers). Do **not** treat git history or prior attempts as free inventory.

This is the same honesty bar as xuss-lame anti-cheat, generalized: a user who aborted mid-flight and wants a **fresh** first ship must get real prompt-to-metal work, not a silent replay of last week’s tree.

| In scope (allowed) | Out of scope (verboten) |
|--------------------|-------------------------|
| Files at **current HEAD** in the product cwd | `git cherry-pick` / `git show oldsha:firmware/…` / restoring abandoned branches for product domain without operator go |
| Operator answers and structured gates | “Previous attempt already had the smiley — I’ll replay that commit” |
| `silico` plate, `board-profile`, knowledge, `parts.toml` / datasheet pointers | Mining `git log` for a prior product-face implementation to skip Stage C–D engineering |
| Host tests you write **in this path** | Other worktrees / stashes / local mid-flight trees of the same GCU used as a code buffet |
| Re-implementing from **this** `spec.md` / README | Training or prior-session memory of a full vertical implementation used to fill a thin/clean-start tree |

**Board still shows a full product face while HEAD is thin (docs/plate only):** that is almost always **stale flash** from an earlier image — not proof that “the code is already here.” Flash **this** build after you implement in **this** tree; then confirm product face against **this** deploy. Do not invent a story that history was “integrated” without the operator asking to continue that attempt.

**Continue a prior attempt (explicit only):** the operator must clearly say something like *continue last attempt*, *use branch X*, *not a clean start*, or *keep the work already on main*. Then that line of history is in scope. **Silent** cherry-pick / replay / “mostly from a previous attempt” is never OK.

**What “done” still means:** host gate + metal acceptance for **this** HEAD. Claiming first ship complete after replaying old commits and re-flashing them is a forbidden close (layered lying).

**Anti-pattern:** Stage D1 “product face works on the bench” + honesty note “mostly from previous attempt commits A/B/C, this session only polished deploy.”  
**Better:** implement face/domain from current `spec.md` + plate + operator; land commits that this session authored (or that clearly continue an **operator-approved** prior branch).

Load on demand: `silico agents --stage head` (or `past-head` / `salvage`).

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
**Better (before deploy/reset):** “About to write firmware to COM7 and soft-reset so the app runs. On this build the product face includes a boot tone for about 15 seconds — expect that, then silence when idle is reached. Ready; deploying now.”

Irreversible writes still need **operator gate** confirmation. Surprising **effects** need **announcement** even when write permission was already granted earlier in the session (permission ≠ “no heads-up on loud audio”).

Violating Bedside on the operator path violates **Agents operate the host path**.

## Part truth: pointers, not documents

Datasheets are free to download and not free to republish, so silico ships **pointers and parsers, never the documents**. Each GCU carries a `parts.toml`: every part the product is built from, and URLs to where its truth lives (datasheet, SVD, devicetree binding, reference driver, errata).

- `silico parts` validates the file (offline, gate-safe).
- `silico parts --fetch` pulls local grounding copies into `.silico/parts/` (git-ignored, per-checkout, disposable). Ground in those before writing hardware-facing code.
- Prefer machine-readable truth when a part has it: an SVD or DT binding beats a 400-page PDF, and community-patched SVDs carry errata the vendor PDFs do not.
- Never commit fetched documents. The licensing problem evaporates only because the user's own tools fetch the user's own copies.

### Board profiles (first-ship product-face pin packs)

Do **not** invent GPIO maps for common boards only from chat or knowledge essays. Silico ships **board profiles** (`silico/boards/*.toml`) with **product face** pin **candidates** (e.g. M5GO-class side strip + speaker).

- Link from `parts.toml` on the board part: `profile = "m5go"` (or `xiao-rp2040`, …).
- `silico board-profile` / `show <id>` — list face candidates.
- `silico board-profile seed [id]` — dry-run seed into `firmware/defaults.py`; add `--yes` only after operator confirms the map.
- Still **operator-confirm product face on metal** (Stage D1). Profile seed is not metal done.
- Detail: [silico/knowledge/board-profiles.md](silico/knowledge/board-profiles.md).

## Make it better than you found it / **compound** (non-negotiable)

Also called **[compound](specs/lexicon.md#compound)** (lexicon name for this tenet). Anytime the path is rough and you had to **guess, correct, reverse, or research** something that a better doc, plate, script, error message, or small infra fix would have prevented for the **next** agent: do not leave that knowledge only in chat. **Compound** before claiming a stage or first ship done (practice GCUs: compound is exit-required).

1. **Notice friction.** Wrong default port, missing UF2 step, bedside eval miss, Windows-only failure, tool flag that changed: if this agent stumbled, the next one will too.
2. **Prefer a durable fix in the right repo.**
   - **Portable operator manners** (contract, surface patterns, CLI init/doctor/eval/ask/step, fixtures, rubric): file and/or fix on **tig/bedside**. Silico is customer 0.
   - **Metal host spine** (ports, deploy, GCU plate, first-ship playbook specifics): fix in **tig/silico**.
   - **Board/host capability knowledge** (ESP32 audio, first-flash, CDC bridges): extend **`silico/knowledge/`** in the same PR when the truth is reusable (see that tree’s README).
   - **Product domain** (idle control, vehicle, product songs): fix in the **GCU** repo.
3. **If you cannot land the fix now, file an issue.**
   - Bedside: gh issue create -R tig/bedside ...
   - Silico: gh issue create -R tig/silico ...
   - Good issues: what you were doing, what went wrong, recovery, proposed change.
4. **Do not soft-fork Bedside principles** into a kinder local AGENTS section. Pin the contract; improve upstream.
5. **Do not invent a parallel spine** in the GCU to avoid filing upstream.

Leaving tribal recovery in chat only violates **Make it better than you found it** / fails to **compound**.

## Getting started for agents (first ship)

When a human says: *See https://github.com/tig/silico. Follow the getting started instructions for agents.*

Run this playbook under **Help the operator**. Confirm each stage with them before advancing.

**One-shot intent:** if the operator already opened the agent **inside the GCU checkout**, stay there. Do not create a second product repo or scaffold into a silico package tree. Silico never encodes a specific product codename; product truth is `spec.md` / product `AGENTS.md` / `README.md`.

### Stage 0 - Welcome the operator (proactive, safe)

Stage 0 is **two steps**. Do not collapse them into “doctor + start gate.” Do not replace them with a self-driven first-ship monologue.

| Step | Name | Deliverable |
|------|------|-------------|
| **0a** | Orientation message | **`silico welcome` output** shown as a **normal chat message** (minimal adapt only) |
| **0b** | Start gate | `bedside ask` / host chooser for go/adjust — **only after 0a is in the transcript** |

**Hard rules:**

1. Do **not** call `bedside ask` / host chooser for `start-first-ship` (or equivalent) until the orientation skeleton has been sent as a normal chat message.
2. Do **not** hand-build 0a from a wall of shell. **Run `silico welcome` first**; that tool is the orientation source.
3. Do **not** open with a tooling-only status dump, then “also orient.” Order is: welcome skeleton in chat → then start gate.

#### Required sequence (do not invent a parallel path)

```text
# TURN 1 — orientation only (read-only; works without GCU bedside.toml)
silico welcome
# paste/adapt skeleton into chat; END TURN — no ask/picker/tool UI after it

# TURN 2 — start gate only (after 0a is a completed chat message)
bedside ask --id start-first-ship --prompt "Start first ship on this machine?" --choices yes,adjust --default yes
# or host picker: same id/prompt/choices; short prompt — no Stage A–C essay

# After go: plate scaffold ships bedside.toml; bedside doctor before metal write gates.
# Do NOT bedside init / vendor third_party into the GCU before 0a+0b go.
```

`silico welcome` is read-only: fills the skeleton from workspace + doctor facts. **Show 0a in chat as its own completed turn** (not only a tool log; not mid-turn text before a host modal), **then** open 0b on the **next** turn.

**Anti-pattern (observed in harness tests):** agent sees missing `bedside.toml` → runs `bedside init` + copies `third_party/bedside` into the GCU → opens start gate with a multi-sentence Stage A–C monologue in the picker → **never** pastes `silico welcome`. That is a failed Stage 0 even if the operator eventually clicks yes.

**Anti-pattern (Claude Code / host UI):** same turn runs `silico welcome`, emits orientation text, then immediately calls `AskUserQuestion` / host picker — operator only sees the modal; agent claims “0a was above the gate.” That fails 0a. Split turns.

**Anti-pattern (free-text cliff):** 0a ends with “Start gate is next” / “Orientation is done” and the session sits on a bare free-text prompt with **no** structured chooser and **no** named human act. That fails 0b and Bedside “never leave them at a cliff.” End 0a with “reply ok/go”; turn 2 **opens the chooser first**.

**Anti-pattern (fetch summarizer):** WebFetch of AGENTS.md returns a garbled digest; agent narrates “summarizer garbled that” and proceeds from partial memory. Re-download full text (or use local clone) before Stage 0.

#### 0a — Orientation (required first operator-facing message)

Be **proactive in a safe way**, but **welcome-shaped**, not systems-report-shaped.

**Primary source:** run **`silico welcome`**. That is the skeleton. Discovery exists so welcome (or a thin fill-in when welcome cannot run) is grounded — discovery does **not** replace the skeleton with agent theater.

**Allowed behind the scenes in 0a** (read-only / non-destructive; prefer letting `silico welcome` / `silico doctor` own it):

- Detect OS; `git` / Python / `gh` / `pip` version checks if welcome did not already cover them
- `gh auth status` (do not start `gh auth login` until after go, unless they already asked)
- Read product `README` / `spec.md` / workspace layout
- List serial ports only as information — **do not** inspect/deploy metal or assume a board identity

**Not allowed before start gate (0b go):**

- Installing packages that rewrite the product tree, changing PATH for the operator, scaffold, deploy, device writes
- **`bedside init`**, copying/vendoring `third_party/bedside` into the GCU, or writing a generic Bedside `AGENTS.md` stub over the product tree
- Destructive git (reset --hard, force-push) unless the operator already ordered that work
- Walls of shell for the human to paste when you could run the check yourself
- **Opening the start-gate chooser** before 0a is visible in chat
- Stuffing Stage A–C / “what happens next” essays into the start-gate `--prompt` / picker body
- Commit, push, PR open, or “full first-ship status” monologue
- Mid-welcome **repo workflow** / PR strategy essays (that is Stage B, after go)
- Long COM folklore tables, multi-section discovery reports, or phase tables that dwarf the skeleton

**Minimal adapt only** (“copy/adapt” means this — not a license to rewrite):

| May change | Must not add before 0b |
|------------|------------------------|
| Fill “this GCU is …” from product docs | Extra tables (ports, PR policy, full doctor dump) |
| Fix a wrong board line if welcome missed it | Mid-welcome commit/push/PR plan |
| Tone to match the session | Parallel “Day 1 drive” install narrative |
| Keep the seven skeleton beats | Tooling-status-first message with orientation buried |

Structure (tone may vary; **skeleton may not** — see **First prompt orients the operator**):

1. **What Silico is** (remind them what they started).
2. **GCU defined + this product summarized** from product docs (or honest “thin docs” note).
3. **Role:** you step them through shipping it on this host and then on the board.
4. **What you know now** — machine readiness **and** workspace mode (GCU root vs silico package vs unknown) **and** whether a preferred USB board is already talking (**short** — one compact paragraph, not a full doctor paste).
5. **Where first ship is headed** — short map: machine tools → product workspace → plate + host tests → board talk over USB (then domain work). Frame first ship as **host plate + device talk**, not host-only. Say **first ship**, not “Day 1.”
6. **Next mutating step** in one short sentence (first step after go), with **why** if it is a big step.
7. **Do not** put the start-gate picker in the same breath as a tooling-only status dump. End 0a by stating that the start gate is **next**.

`silico welcome` prints this skeleton (plus a doctor snapshot). Lightweight eval: thin first turns that only list tooling fail the same markers the welcome tests enforce (tig/silico#70).

Example shape (0a only — no start-gate tool yet):

> Welcome. **Silico** is the open host-first spine for building shippable edge products: agents build and maintain products on real boards; Silico is the host tooling and plate, not the product brand.
>
> This session builds a **GCU** (GCU stands for General Contact Unit — Silico’s term for one shippable edge product: app + board). From the product docs, this GCU is: …
>
> I'm here to get it shipped. I step through host setup, plate, tests, and the board. **I own the host path**; the operator owns product judgment and confirms physical or irreversible steps.
>
> On this machine I already checked: Git OK, Python 3.12 OK, gh logged in; workspace mode=gcu (we stay in this product checkout); preferred board not on USB yet (only a demoted adapter).
>
> **first-ship map:** (A) machine tools → (B) workspace locked → (C) **plate** (standard project template) via **scaffold**, then **host gate** (automated tests on this computer) green → (D) board talks over USB and a confirmed first deploy. We do not stop at host-only.
>
> **Next after go:** ensure a **local clone** of Silico on this machine, editable-install it, then scaffold/merge the plate here — that gives us the maintainable repo layout and an honest host test path before we touch the board.
>
> Orientation is done. **Start gate is next.**

#### 0b — Start gate (only after 0a)

Ask whether to start or adjust something with **`bedside ask`** (preferred when CLI works) or the host **structured question UI** under the **same contract** (short prompt, recommended first, **decline = halt** — see **Operator gates**). Not a multi-option free-text paragraph. Not a status essay with a chooser stapled on.

Only after a clear **go** (or after applying their adjustments and **re-confirming** with another gate) may you begin **mutating** Stage A work (installs, scaffold, repo create, device paths).

If the answer is **adjust** or **no** / exit **10**: **halt writes** — short re-gate or stop. Do **not** keep mutating and monologue a full first-ship status.

**Anti-pattern:** promising to stop after host gate and "check back before we go near the board." Host gate is a checkpoint, not first ship done. After go, you drive through Stage D prep (USB talk + REPL) unless the operator explicitly defers metal.

**Anti-pattern:** first message that only lists tooling status with no Silico explanation and no GCU summary.

**Anti-pattern:** `bedside ask --id start-first-ship` (or host chooser) as the **first** operator-facing act, before orientation is in chat.

**Anti-pattern:** wall of shell discovery → hand-built multi-section orientation → host picker with a prose wall → operator declines → agent still commits/pushes and pastes a full first-ship report. That is the failure mode this section exists to prevent.

**Anti-pattern:** `bedside doctor` fails → note it → never call `bedside ask|step` again for the rest of the session.

### Stage A - Machine prerequisites

When a human must install or approve something, use **Big steps: why + where** (Stage A — machine tools on this host; next is locking the product workspace).

1. Detect OS (Windows / macOS / Linux). Tell them what you detected in one sentence.
2. Ensure **Git** is installed and on PATH. Install if missing; verify with a version command you run.
3. Ensure **Python 3.11+** (`py -3` on Windows, `python3` elsewhere). Install/guide if missing; do not assume `python` means 3. Do not install EOL 3.9/3.10 as the project floor.
4. Ensure **GitHub CLI (`gh`)** is installed. Install if missing; verify `gh --version`.
5. Ensure **pip** works for that same Python.
6. Summarize ready vs needs a human click. Stop cleanly if an installer UI requires them.

### Stage B - Workspace lock (GCU root) and GitHub identity

**Where we are:** Stage B — product workspace (after machine tools). Goal: one clear GCU root; no second invented repo.

**B0 — Lock the product workspace (do this before inventing a repo):**

1. Run `silico doctor` (or detect markers): `spec.md`, `silico.toml`, `firmware/`, product `AGENTS.md`.
2. **`Workspace mode: gcu`** → **cwd is the product root.** Do **not** ask “create a new repo?” Do **not** clone elsewhere. All scaffold/deploy work stays here.
3. **`Workspace mode: silico-package`** → you are inside **tig/silico**. Do **not** scaffold a customer GCU into this tree. Ask the operator to open/create the product checkout, or only work on silico itself if that is the task.
4. **`unknown`** → empty dir or unrelated tree: then Stage B1 (create/clone product).

**B1 — GitHub identity (when a remote product repo is needed):**

1. Check `gh auth status`. If not logged in, walk them through `gh auth login` **one prompt at a time**.
2. If cwd is already a git GCU with `origin`, use it.
3. If create new: confirm a product or codename (**not** `silico`); `gh` create private; clone **or** init in the empty cwd.
4. Remind them: silico stays `github.com/tig/silico`; **their product** is the GCU repo.
5. Once the GCU remote is known: **inspect repo workflow** (branches / PRs / issues) and apply **Repo workflow: inspect, then choose main vs PRs** before the first push. If remote is **tig/xuss**, **tig/xuss-c**, or **tig/xuss-lame**: **main only** (no PR chooser); **verify clean start** tip before mutating (see that section).

### Stage C - Local silico checkout, pin, and scaffold the GCU

**Where we are:** Stage C — get a **local Silico clone** on this host, editable-install the CLI, **scaffold** the **plate**, green the **host gate**. Next after green: Stage D (board talk), not “done.”

**Do not hand-invent a parallel spine.** Use the package + plate. **Always `silico scaffold .` from the product root** (Stage B0), never from a silico package checkout.

1. **Local Silico checkout (not “pip install from GitHub”).** first-ship agents **clone** `tig/silico` onto the machine (once) and install from that path so host tools do **not** re-hit GitHub over HTTPS on every `pip install`.

   **Find or clone:**

   1. If cwd is already a **silico-package** checkout (or you are only working on silico itself): use **this** tree. Do not clone a second copy for that work.
   2. If cwd is a **GCU**: look for an existing clone (common: sibling `../silico` under the same parent as the GCU, e.g. `…/tig/silico` next to `…/tig/xuss-lame`).
   3. If missing: clone beside the GCU (or into the operator’s usual source root) with authenticated git / `gh` — **not** by asking pip to fetch the package:

```text
# From the parent of the GCU (example layout):
gh repo clone tig/silico
# → ./silico  next to  ./<gcu>
```

   **Editable install from the clone** (package name **`tig-silico`**, CLI still `silico`):

```text
python -m pip install -U pip
python -m pip install -e "/path/to/tig/silico" pytest
python -m pip install -e "/path/to/tig/silico/third_party/bedside"
# Never: pip install silico  — unrelated PyPI package (issue #27).
# Never first-ship bootstrap:  pip install "tig-silico @ git+https://github.com/tig/silico.git@…"
#   That forces HTTPS to GitHub on install and is not the intended host path.
```

   **GCU `requirements-dev.txt` pin** — local path, not a git URL:

```text
# Host-only. Prefer editable local clone (sibling layout is typical).
-e ../silico
pytest>=8
mpy-cross==<pin matching device MicroPython major.minor — see below>
```

   Use the real relative or absolute path to **this machine’s** clone. After scaffold, rewrite plate defaults if they still show a remote git URL.

**Checkout / pin rules:**

| Fact | Rule |
|------|------|
| first ship host path | **Clone once** (`gh repo clone tig/silico` or equivalent) → `pip install -e <clone>`. |
| Why not git+https pip pins | Every install re-talks to GitHub; auth/rate-limit/offline failures; wrong mental model (“Install silico” from the network). |
| Package version (e.g. `0.1.4` in `pyproject.toml`) | Dist metadata only. `silico doctor` saying `tig-silico 0.1.4` does **not** mean invent `@v0.1.4`. |
| Git tags `v0.1.3` and earlier | Pre-rename (`name=silico`); do not use as a `tig-silico` pin. |
| CI host gate | Plate ships `.github/workflows/ci.yml` that checks out the GCU and **`tig/silico` as siblings** (`path: gcu` + `path: silico`) so `pip install -r requirements-dev.txt` still uses `-e ../silico`. **Do not** invent `silico-src` workarounds or skip `requirements-dev.txt` on the runner. |

If clone or editable install fails, **stop**, say what broke, and file/fix on `tig/silico`. Do **not** vendor host tooling into the GCU. Do **not** thrash invented version tags or remote pip URLs as a workaround.

**mpy-cross pin (ABI) — Silico owns this chain:**

Product specs must **not** name a MicroPython version or hand-derive the PyPI pin. That is board/toolchain knowledge.

1. Plate defaults ship a **recent stable** PyPI `mpy-cross` as a starting point only.
2. After the board talks: `silico inspect --port COMx --apply-mpy-pin` — Silico reads device MicroPython **from `sys.implementation`**, maps to an installable pin, and writes **both** `silico.toml` `[runtime].mpy_cross` and `requirements-dev.txt`.
3. Refuse/warn on **ancient** device images; first-flash a current port before applying pins.
4. Packaging: install **`tig-silico`** from the **local clone** (`pip install -e …`), never bare `pip install silico`.
5. `silico doctor` warns on ancient plate pins. Fix before claiming the host compile gate is honest.

2. Scaffold the plate (merge into existing GCU is OK; product `README.md` / `spec.md` are never overwritten):

```text
silico scaffold .
# empty dir also fine: silico scaffold ./my-gcu
# C / ESP-IDF plate (issue #53): silico scaffold . --plate gcu-c
# --force overwrites non-protected plate files only (not README/spec)
```

3. If `spec.md` exists: **assess contract quality first** (see **Spec interview mode**). When thin or contradictory, run the interview / interactive-path gate **before** treating the contract as product truth for identity or domain. Do **not** invent moat or pick winners among conflicting fields.
4. Set product identity in `firmware/version.py` and `silico.toml` from **product files** when present (README title, `spec.md` identity lines) **only after** identity-relevant contradictions are resolved, **or** the operator chose interactive path and named an **explicit** identity assumption. Until then leave plate defaults; do not persist a guessed name/version from an unresolved contract.
5. If the contract (post-interview / settled assumptions) is good enough for the current slice: host gate proves the **plate + product path** first; domain behavior comes from the **product** spec/AGENTS (not invented in silico). Open host knowledge topics only when the product needs board caps (e.g. `silico/knowledge/esp32-audio.md` for DAC/speaker work).
6. Run host gate until green: `python -m pytest -q` (or `silico doctor` then pytest / `silico gate` / `silico product-path`).
7. Commit and push using the **repo workflow** you already inspected (see **Repo workflow: inspect, then choose main vs PRs**): simple repos → recommend **main**; well-used → confirm PRs vs main with the operator. Further first-ship work continues as **more commits on that same branch/PR**. Confirm CI/Actions is on; if on a PR path, **watch CI green** before treating remote as proven.
8. **Do not stop here.** Host gate green is a checkpoint. **Immediately continue into Stage D**.

### Spec interview mode (under-specified or contradictory `spec.md`)

**Issue:** [tig/silico#68](https://github.com/tig/silico/issues/68). Detail: [silico/knowledge/spec-interview.md](silico/knowledge/spec-interview.md).

After go, when you read product `spec.md` (or the product says the contract lives there):

**If the contract is good enough** — readiness layers, hardware fix, product face, scary rails, and acceptance rows that do not fight each other — **do not** interview. Build.

**If the contract is way under-specified or overly contradictory**, do **not** pretend the path is clear and invent domain moat. Enter **interview mode**:

1. **Detect (lightweight):** thin (missing layers / hardware fix / product face / rails / acceptance); contradictory (same key two ways; acceptance rows that cannot all be true); silent on scary surfaces (long audio, force channels, escape hatch, dead-man).
2. **Gate with the operator** (structured chooser first): recommended path **interview gaps now**, or **proceed interactively and improve the spec as we build**, or adjust.
3. **Interview:** one gap (or tight cluster) at a time; recommended option first when plate/parts/knowledge give a defensible default; free text only for open domain judgment.
4. **Capture:** propose `spec.md` edits only after operator **yes**; or durable issues / ambiguity log if they prefer. Chat alone is not enough when the next agent must re-guess.
5. **Do not persist product identity** into `firmware/version.py` / `silico.toml` from conflicting or unresolved identity fields — assess and settle (or take an explicit interactive assumption) first (Stage C steps 3–4).
6. **Exit interview when:** blocking fights resolved, **or** operator chose interactive path, **or** remaining gaps are named follow-ups.

**Interactive path (operator opt-in)** — they may say roughly:

> Spec is incomplete; that is OK. Start building interactively. We will improve the spec as we go. I can re-run you later to rebuild once the contract is stronger.

Then: do **not** claim the product is fully specified; implement the current slice host-first with **explicit assumptions**; accumulate gaps; **late step** offer spec edits (same as Spec gaps below). Re-run / rebuild later is expected as the spec improves.

**Anti-patterns:** block forever on a perfect spec; invent vertical moat without judgment; free-text choice walls; skip metal poll when metal is in scope; leave recovery only in chat.

**Practice GCU (maintainers / interview dry-run):** private [tig/xuss-lame](https://github.com/tig/xuss-lame) is a thin, messy first-draft product tree (not labeled as a test in-repo). When first ship is aimed at that checkout, product truth is **only** that tree + the operator — do **not** open `tig/xuss` or `tig/xuss-c` (or use prior knowledge of them) to “complete” the contract. Detail: [silico/knowledge/spec-interview.md](silico/knowledge/spec-interview.md). Repo workflow for **xuss / xuss-c / xuss-lame**: always **direct-to-`main`**; confirm **product-only clean start** on `origin/main` before first-ship mutates (see **Repo workflow** → Maintainer practice GCUs).

### Stage D - Talk to real hardware (hello metal)

**Where we are:** Stage D — hello metal. Host plate and host gate are behind you; first ship is not done until the board talks, a confirmed deploy runs, and the **operator can see or hear** the product doing something that matches documented “good.”

**Required for first-ship exit** (not optional polish). Goal: board **talks over USB**, is **prepped** (REPL when that is the runtime), then a **distinct, documented, operator-observable product face** (what the operator sees or hears when the app runs); reconnect is **repeatable**.

**Product face code** must come from **this HEAD** (or an operator-approved continue path) — not past-HEAD salvage of a previous attempt. See **Product truth is HEAD**.

Metal COM / first-flash / identity / deploy rules: **[BEDSIDE.md](BEDSIDE.md)** + **[silico/knowledge/first-flash.md](silico/knowledge/first-flash.md)**. USB duplex / lockout: **[silico/knowledge/esp32-usb-serial.md](silico/knowledge/esp32-usb-serial.md)** (open only when needed). Prefer tools: `silico wait-device`, `inspect`, `pull`, `deploy`, `monitor`, and `bedside ask` / `bedside step`. Every physical or overwrite prompt uses **Big steps: why + where**.

#### Stage D0 - Device talks (prep) before any deploy plan

Until true, device is **not** prepped:

1. A real poll shows a candidate (`silico wait-device`, often `--timeout 300`) **or** operator names a port after `silico doctor` (ESP-class CDC may score as preferred; still confirm identity).
2. `silico inspect --port COMx` proves modern REPL **or** you walk **first-flash once** (UF2 **or** esptool — see knowledge/first-flash).
3. Operator confirmed **this port is the product board** (`bedside ask --id confirm-board …` or host UI; default **no** if unsure).
4. Only then: dry deploy → `bedside ask --id confirm-deploy …` → `--yes --verify --reset` → **soft-reset again if the app loop is not running** (verify parks the REPL).

**If the board was missing at Stage 0:** after host gate, ask only for the data cable plug, then **immediately** run a long `wait-device` poll.

**Anti-pattern:** host gate green + "hardware later" with no wait-device/inspect/REPL proof.

##### Serial readiness ladder (before tool-hostile console)

Host gate green ≠ duplex OK. **TX/telem/identity alone is not metal OK.**

1. Stock (or known-good) raw REPL via `silico inspect`.
2. Deploy product **without** `micropython.kbd_intr(-1)` until step 3–4.
3. Prove **round-trip**: host line → device response (not outbound-only spam).
4. Only then: Ctrl-C-is-data + working `repl`/`reboot` door; prove `repl` restores mpremote.
5. Then product face observe (D1).

**Lockout:** door dead / cannot enter raw REPL → **do not thrash redeploy**. Recover **once** (esptool erase+write or UF2), park stock MicroPython, fix duplex on the host, then redeploy. CLI prints the recipe (`LOCKOUT_RECOVERY` / #62).

#### Stage D1 - Operator-observable acceptance (not version-string theater)

Deploy verify + `FW_VERSION` match prove the **host wrote this build**. They do **not** alone prove first-ship metal.

**Metal is honest only when:**

1. There is a documented **product face** — the **“good”** the operator can **see or hear** without serial folklore (product `spec.md` / `install/`: LEDs, boot riff, status pattern, etc.). Define **product face** on first use if not already defined this session.
2. After soft-reset so the app runs, you **ask the operator** (structured gate or one plain yes/no they answer from the world in front of them) whether that product face is true.
3. If product docs name a product face (e.g. M5 front-panel / side LEDs, speaker riff) and the plate only toggles a generic/dev-board pin (e.g. XIAO GPIO LED that is not the product face): **that is HW confusion, not first ship done.** Resolve it with the operator — prefer **`silico board-profile`** pin packs (e.g. `m5go`: side strip **15**, speaker **25**) and `silico board-profile seed` into `firmware/defaults.py` **after** operator confirm of the map; also use parts/spec/board knowledge. Host-test, redeploy, re-confirm observe. Filing a GitHub issue is a tracker, not acceptance.
4. Product face gaps that block observe are **in-scope first-ship metal work**. Silico exists to help the operator through this. Do not label the session “on the metal” / “first ship complete” while an open issue still says the product face is unproven.

##### GPIO / pin / product face ambiguity → **stop and ask** (mandatory)

When you notice (or should notice) that the **pin, LED, speaker, or product face “good”** in firmware does not clearly match the **product board / spec**, you **must not** quietly assume, monologue an “Honesty” paragraph, or only open a GitHub issue. Never call this bare “face.”

**Required path:**

1. **Stop advancing** Stage E/F claims. Stay in Stage D metal acceptance.
2. **State the mismatch in plain language** (what the code drives vs what the product docs say the product face should look/sound like).
3. **Ask the operator to clarify** with a **structured chooser** (`bedside ask` or host picker) — or one focused free-text question only if the answer is open (e.g. “which LED on the M5 front panel is the product face status light?”). Put the **recommended** guess first when you have one from **`silico board-profile`** / parts/spec/knowledge (e.g. `silico board-profile show m5go`).
4. Only after their answer: implement the mapping, host-test, redeploy, then **confirm observe** (“Do you see/hear X?”).
5. Optional: file/update an issue **as a tracker after or while** you are driving the clarify → fix loop — never instead of asking.

Example gate shape (use host picker / `bedside ask`, not a free-text `1/2/3` wall):

```text
bedside ask --id clarify-product-face \
  --prompt "Plate hello blinks GPIO16 (often a small module LED). Product docs want M5 front-panel or side lights as the product face. Which should we treat as first-ship good on this board?" \
  --choices "m5-front-panel-led,m5-side-led,gpio16-ok-for-now,operator-will-point" \
  --default m5-front-panel-led
```

**Anti-pattern:** agent notices wrong GPIO, writes “Honesty: not the M5 product face LED,” files `#5`, and asks “merge PR or start domain?” without ever asking the operator which light/sound is correct. That **strands** the operator and violates Help the operator / scary surfaces.

**Anti-pattern (forbidden claim):** title or summary like “GCU is on the metal” + an “Honesty” section that admits the product face was **not** proven. That is layered lying: call the layer you proved (`deployed` / `REPL ready`) and leave metal-acceptance open.

**Allowed partial claim (honest):** “Board talks on COM7; deploy verified XUSS 0.0.1; product face LED mapping is unclear — I need you to clarify which light is first-ship good before we call metal done.” Then run the clarify gate **in that same turn**, not later.

**Stage D steps (order only — details in BEDSIDE + knowledge/first-flash):**

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
9. Document `install/` leave-behind (update-path one-liner + product face “good”: LEDs/audio/etc.).

Non-Python deploy assets (e.g. audio riffs) may appear in `[deploy].core`; host hygiene skips them as copy-only.

### Stage E - CI proves metal change

1. Ask the human to open a GitHub Issue on the **GCU** repo (or create with `gh` after approve). Title example: `Change the firmware blink pattern (distinct A vs B)`.
2. Implement: firmware behavior change **and** host tests/CI green. Domain follows product `spec.md` when present.
3. Push commits to the **existing** first-ship branch/PR (or open the first PR if none yet). Do **not** open a new PR per stage. Watch CI; fix red builds.
4. Deploy only after operator confirmation again if overwriting; confirm the visible/audible acceptance matches the issue.
5. Close the issue with a short note linking the commit/PR.

Closed loop: **issue → agent → host gate → CI → metal**.

### Stage F - Domain work (still first ship)

1. Human points at domain intent (docs, notes, rough brief). You do **not** invent the vertical moat.
2. Write detailed specs, tests, and `firmware/` under test-first and host-first rules.
3. Staged plan as **cross-linked, tagged GitHub Issues** for proprietary work — **issues stage work, not a PR per issue** unless the operator asked for multi-PR staging.
4. Host gate green locally before claiming done. Flash only confirms.
5. Push more commits to the same branch/PR; CI matches local. Change requests arrive as GitHub Issues. Implement them without requiring the human to know git branches unless they want to.

#### Spec gaps

While coding, treat product `spec.md` items that are lacking, confusing, or wrong. **start-of-first-ship** thin/contradictory contracts use **Spec interview mode** (above). Mid-build gaps use this table.

**Split by whether the gap blocks operator-observable metal:**

| Gap type | Rule |
|----------|------|
| **Blocks see/hear acceptance** (which LED is the product face, pin map for this board, boot riff, “what good looks like”) | **In-scope now.** **Ask the operator to clarify** (structured gate) as soon as you notice the mismatch — do not only monologue or file an issue. Then parts.toml / knowledge / board docs / implement + confirm. Spec rewrite can still wait, but **bench truth cannot**. |
| **Domain polish / later product depth** (full protocol, vehicle table, extra modes) | Do not block the current host-green slice. Note the gap; **late step** offer a proposed `spec.md` edit after host gate is green or at a stage boundary. |

For non-blocking gaps (and after **interactive path** from interview mode):

1. Prefer configurable defaults, explicit assumptions in code/issue comments, and host tests.
2. Quietly note gaps (issue comment or checklist).
3. **Late step** — prompt the operator: what was wrong/missing, a proposed edit, and ask (structured chooser) whether to update the spec **now**.
4. Edit the product spec only after a clear **yes**.
5. Expect re-run / rebuild later when the operator chose interactive path and the contract later gets stronger.

### Review pass per product slice (recommended)

After each meaningful product slice (plate green, audio path, UI face, link door, …), run an **independent review** of that slice’s diff before claiming host-done or stacking the next domain change (#79 field report). Compile + ctest + CI miss boot-paint and HAL-init drops that a focused review catches. Costly in tokens; cheaper than a silent metal miss.

### first-ship exit criteria (before the update path)

Metal bar detail: [BEDSIDE.md](BEDSIDE.md). Spine/DoD: layered table below.

- [ ] **Device talks over USB** (`silico inspect` / REPL) and was **prepped** (runtime once if needed).
- [ ] **Operator-observable metal:** after confirmed deploy + app running, the operator can **see or hear** the documented **product face** for **this** product (not only a plate pin that is not the product face). Agent worked through HW confusion; did not stop at version match + issue filed.
- [ ] Host gate green locally and on GitHub.
- [ ] Device `FW_VERSION` matches host.
- [ ] One documented update path (BEDSIDE update-path leave-behind) that states what good looks/sounds like.
- [ ] Silico pinned as host dependency.
- [ ] Operator helped through first flash/serial without assumed ops expertise.
- [ ] Any “what next?” stage fork used a **structured chooser**, not a free-text numbered menu.
- [ ] **Compounded:** friction from the path landed as a durable fix/issue (not chat-only). Required for practice GCUs (xuss / xuss-c / xuss-lame).

**Not exit criteria:** host gate alone; scaffold alone; deploy verify / version match alone; deferred metal with no poll/inspect; “honesty” note that the product face is unproven while the title says on-the-metal; issue filed instead of resolving observe.

**Update path:** same update path; unit to field test or field trial.

## Definition of done (layered)

Host-first is **not** host-only. Claims must name the layer they prove:

| Layer | Claim example | Required proof |
|-------|---------------|----------------|
| **Host** | Domain logic / sim / plate | Named host gate green (default: `pytest -q`). CI green if remote exists. |
| **Metal I/O** | Sensing or actuation on pins | Inject/measure on **named** pins (or harness signature), not only LED blink or version import. |
| **Vehicle / field** | Product acceptance on real plant | Product Appendix / field procedure; not bench buzz alone. |
| **Deployed** | Board runs this build | Device `FW_VERSION` matches host after confirmed write; optional harness OK. **Not** the same as product metal acceptance. |
| **Metal accepted (first ship)** | Product on the bench | Operator **sees or hears** documented **product face** for this GCU; pin / product face confusion resolved or explicitly deferred as **not first ship complete**. |
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
| `inspect` | Serial identity knock (not mpremote); no `--apply-mpy-pin`. Default: DTR/RTS **deasserted** first, re-knock over a short window, pulse only as fallback (#78 / #79) |
| `deploy` | `idf.py build` + flash; plan says full image overwrite; `--prune` / `--verify-import` refuse |

**C identity-on-link (hard):** the image must **answer** `identity` on the UART with `fw_name=… fw_version=…`. Boot-print only is not metal inspect-ready once the banner scrolls past. Plate `gcu-c` documents and implements the knock responder.

Default plate stays MicroPython. Arduino is not this path (see issue #59). First consumer for C first ship is **tig/xuss-c** (spec-first product; not closed by hello-metal alone).

### Forbidden closes

- Do **not** close a **P0 sensing/actuation** issue as done with only host/sim code if the device path is still a stub (`pass`, empty IRQ, no feed into the estimator). Either:
  1. land metal code that proves the pin path, or
  2. leave a **blocking metal follow-up** open (title/status makes metal-TODO obvious) and do not narrate the product as metal-ready.
- Do **not** mark vehicle/Appendix acceptance done without the vehicle procedure (or explicit defer with open tracker).
- Do **not** mark first ship / “on the metal” done when the operator cannot see or hear the **product face**, even if deploy verify and version match passed. Filing “product face LED wrong pin” and moving to Stage F is a forbidden close.
- Do **not** notice GPIO / product face mismatch and skip asking the operator to clarify (honesty note or issue alone is not a clarify gate).
- Do **not** invent short forms of lexicon terms (e.g. bare “face” for **product face**) in operator-facing prose.
- Do **not** present stage forks as free-text `1. / 2. / 3.` menus in chat when a structured chooser exists (or `bedside ask` is available).
- Do **not** invent a PR workflow on a quiet/simple GCU without asking — recommend **main** first (see **Repo workflow**). Do **not** invent a PR path on **tig/xuss**, **tig/xuss-c**, or **tig/xuss-lame** (always main; check clean start first). Do **not** open a fan-out of PRs for sequential first ship / same-session work unless the operator asked to stage multi-PR.
- Do **not** implement or claim product face / domain by **past-HEAD salvage**: cherry-pick, replay, or copy firmware from older commits, other branches, stashes, or prior attempts without explicit operator go to continue that line (see **Product truth is HEAD**). Applies to every GCU clean start and abort-and-retry, not only practice trees.
- Do **not** treat a board still showing a full app while HEAD is docs/plate-only as “code already landed” — re-flash **this** build after implementing in **this** tree.
- Do **not** deploy, soft-reset, or otherwise drive metal that may play loud/long audio, flash bright patterns, or move actuators without a clear operator-facing forewarning of what will happen and for how long.
- Do **not** claim metal serial OK from identity/telem TX alone, or enable `kbd_intr(-1)` before round-trip + working `repl` re-entry (see serial readiness ladder; #62).
- Do **not** thrash full-erase/redeploy when the console is locked; recover once, park stock MP, stop.
- Do **not** skip `silico welcome` / `bedside ask|step` (or same-contract host gates) in favor of a self-driven first-ship monologue or hand-built status dump.
- Do **not** treat “Prefer doing over instructing” as permission to mutate past an open or declined operator gate.
- Do **not** continue commit/push/deploy/scaffold after gate exit **10** / operator **no** / **adjust** without a new clear go.
- Do **not** stuff why/where essays into the gate prompt body; keep the chooser one step.
- Do **not** note `bedside doctor` failure and invent a pre-go vendor/`bedside init` path — show `silico welcome` (0a) first; fix the pin after go via plate.
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
| `specs/prfaq.md` | v1 Working Backwards (PR + FAQ) |
| `specs/silicov1.md` | v1 build spec |
| `specs/gcu-codenames.md` | Public GCU codenames only |
| `specs/lexicon.md` | Phrase book |

Prefer [silicov1.md](specs/silicov1.md). Do not invent a second architecture.

## GCU vs silico

| | **silico** (`tig/silico`) | **GCU** (private product repo) |
|--|---------------------------|--------------------------------|
| Owner | Open spine | Vertical product |
| On metal | No | `firmware/` yes |
| Host pin | N/A (is the package) | `requirements-dev.txt` pins **local** silico clone (`-e ../silico`) |
| Domain IP | Never | Always |
| Public names | Zakalwe, Quilan, Sma (codenames) + short published shape when the owner chooses | Full domain IP stays in the GCU |

When a second GCU needs the same host machinery, promote into silico and bump the pin (**Extract, then open**).

## Confidentiality

Public Silico docs name starter GCUs **Zakalwe**, **Quilan**, **Sma**. Short product shape and builder attribution may appear when the owner publishes them (see [gcu-codenames.md](specs/gcu-codenames.md) and README Real World Examples). Do not invent extra brand/market detail or dump private domain IP into the spine.

## What not to do

1. Do not put product domain logic into silico to win a demo.
2. Do not require the human to hand-author firmware as the default path.
3. Do not assume the human can flash initial firmware, pick ports, or run agent/shell tricks without being taught in the moment.
4. Do not dump unexplained command walls; do not say "run this" when you could run it.
5. Do not skip host gate or CI because metal "looked fine."
6. Do not use blind serial auto-connect on multi-device hosts.
7. Do not invent a PR workflow on a simple/quiet GCU without asking (recommend main first); do not open many PRs for one first-ship path unless the operator asked to stage multi-PR.
8. Do not surprise the operator with metal effects (loud/long tones, motion, sudden reboot loops) without clearly announcing what will happen first.
9. Do not deploy host `sim/` or silico package modules to the board.
10. Do not claim external adoption or platform status without scoreboard evidence.
11. Do not rewrite PR titles, Grady quotes, or Tig quotes unless the human asks.
12. Do not start Arduino / multi-runtime work unless a GCU forces it (v2).
13. Do not burn an hour recovering from silico friction and leave no issue or doc fix for the next agent.
14. Do not treat manners tools as optional: skip `silico welcome`, skip/abandon `bedside ask|step`, or replace Stage 0 with a host-tool install script narrative.
15. Do not keep mutating (commit/push/scaffold/deploy) after an operator gate decline / exit 10; halt, short re-gate, or stop.
16. Do not read “Prefer doing over instructing” as “drive past the operator’s gates.”
17. Do not past-HEAD salvage product domain (cherry-pick / replay prior attempts / git archaeology for firmware) on first ship or clean start without explicit operator go to continue that line.
18. Do not treat stale board flash as proof the current tree already contains the product face.

## Commands (host)

Run these yourself when possible. Show the human only what they must see.

```text
# Host spine: local clone of tig/silico, then editable install (Stage C).
# Package: tig-silico. CLI: silico. Not `pip install silico` (unrelated PyPI name).
# Prefer: sibling clone or `gh repo clone tig/silico` — not git+https pip pins.
python -m pip install -e "/path/to/tig/silico" pytest
python -m pip install -e "/path/to/tig/silico/third_party/bedside"
# when already inside a silico checkout:
python -m pip install -e ".[dev]"
python -m pip install -e ./third_party/bedside

silico welcome          # REQUIRED Stage 0a FIRST (paste to chat, then start gate; works without bedside.toml)
# bedside doctor        # after go / before metal write gates — not a pre-0a blocker
# bedside eval
# operator gates (required path; host structured UI OK only under same contract):
# bedside ask --id start-first-ship --prompt "Start first ship on this machine?" --choices yes,adjust --default yes
# bedside ask --id confirm-board --prompt "Is COMx the product board?" --choices yes,no --default no
# bedside ask --id confirm-deploy --prompt "Overwrite firmware on COMx now?" --choices yes,no --default no
# bedside step --id plug-usb --prompt "Plug a data USB cable." --expect "Board shows power / new COM."
# exit 10 / decline → halt writes; do not monologue past no
# missing pin after go → plate bedside.toml / sibling vendor; never invent prose path
silico doctor
silico wait-device
silico scaffold .
python -m pytest -q

silico inspect --port COMx
# plan only (no write); --port required; prefer silico.toml [deploy].core with no file args:
silico deploy --port COMx
# AFTER bedside ask (or equivalent) confirms identity + write:
# live PROGRESS [write] i/n name (size) lines stream as each file copies
silico deploy --port COMx --yes --verify
# first-flash MicroPython once (esptool progress streams; or UF2 with --uf2-dest):
# silico first-flash ESP32_GENERIC-….bin --port COMx --yes
# silico first-flash board.uf2 --uf2-dest E:/board.uf2 --yes
```

Always pass explicit `COMx` / `/dev/tty...` to deploy. Confirm device identity every session via `bedside ask` (or host picker), not chat multi-choice walls.

## When working in silico itself

1. Re-read `specs/` files before editing them.
2. Prefer surgical edits over rewriting whole docs.
3. Preserve human-owned wording (PR title, Grady quote, Tig quote).
4. Commit in small, reviewable steps when the human wants revision history.
5. Host gate for silico package code when it exists; docs-only changes need no metal.
6. Apply **Make it better than you found it** here first: doc and infra PRs in this repo beat issues when you already have write access.
7. Follow Tig's writing style.
