# AGENTS.md - GCU product

Guidance for AI coding agents in **this product repo**.

## FIRST ACTION (first ship / getting started) — do this before any status dump

When the human says *follow silico getting started* (or first ship / Day 1):

0. **Open the silico spine AGENTS** (local `../silico/AGENTS.md` or raw `https://raw.githubusercontent.com/tig/silico/main/AGENTS.md`). The GitHub README/homepage alone is **not** the agent playbook.
1. **Do not** open with tooling narration, `bedside init`, vendoring `third_party/`, PR strategy, or a start-gate chooser.

```text
silico welcome          # 0a FIRST — paste as first operator chat message (tool log only fails 0a)
bedside ask --id start-first-ship --prompt "Start first ship on this machine?" --choices yes,adjust --default yes
# host picker: same id/prompt/choices only — never invent Go / Host-only / Look around
```

2. **0b** only after 0a is in chat. One short question; choices **yes** / **adjust** only. Host picker: say once.
3. **Decline / exit 10:** halt writes; short re-gate or stop.
4. **After go:** plate / sibling silico paths for manners pin — not pre-go vendor.

Full playbook: silico root `AGENTS.md` FIRST ACTION.

## Spine

Host path comes from **silico** (https://github.com/tig/silico). Pin as host-only. Device `firmware/` never imports silico.

Operator manners follow **Bedside** (`bedside.toml` in this repo points at the sibling silico vendor paths). Metal notes: `BEDSIDE.md` here + silico `BEDSIDE.md` / knowledge. Silico-specific operator language (define jargon on first use; big steps need why + where-we-are) lives in silico root `AGENTS.md` → **Operator language**.

first ship is **host gate + device USB talk/prep**, not host-only. After scaffold and green pytest, continue into `wait-device` / `inspect` / REPL (or UF2) unless the operator explicitly defers metal.

**Spec quality:** if product `spec.md` is way under-specified or contradictory, enter silico **spec interview mode** (root AGENTS + `silico/knowledge/spec-interview.md`) or take the operator’s **interactive path** (build while improving the spec; re-run later). Do not invent domain moat. Product truth is **this** checkout + the operator — not a sibling GCU repo with a similar name.

## Help the operator

Assume low ops literacy. Prefer doing over dumping shell. **Poll USB** after asking for a data cable - do not ask humans to announce plug-in. **Confirm device identity** every session. **Never write the device without explicit operator confirmation.**

**First-use terms:** the first time in a session you say GCU, host, plate, scaffold, gate / host gate, metal, **product face**, pin, or deploy — define it in plain language (parenthetical). Full book: silico `specs/lexicon.md`. Use **canonical lexicon names** only — never invent short forms (e.g. bare “face” for product face).

**Big steps:** when asking the human to install, log in, plug hardware, first-flash, or confirm overwrite — one sentence **why**, one line **where we are** on first ship (phase + done vs next), then the single act.

**Next-step forks:** use a structured chooser (`bedside ask` or host picker). Never a free-text `1. / 2.` menu in chat.

**Repo workflow:** inspect the GCU remote (branches / PRs / issues). **Simple** tree → recommend commits on `main` (PRs later). **Well-used** → ask whether to use PRs (note: CI/CD proof is then an explicit PR step). Never PR-spam: one branch/PR per first-ship path max unless the operator asked to split. Issues stage work; commits stage history. Full rule: silico root AGENTS **Repo workflow**.

**Metal acceptance:** first ship is not “on the metal” until the operator can **see or hear** the documented **product face** after deploy. Wrong plate pin / product face LED confusion is work to finish with the operator — not an honesty footnote under a done banner. Trackers do not replace observe. **If the pin / product face mapping is unclear, ask the operator to clarify (structured chooser) in that turn** — do not only file an issue or assume GPIO16 is fine. Prefer **`silico board-profile`** pin packs (link `profile = "…"` in `parts.toml`; `seed` into `defaults.py` after confirm) over inventing M5 side/speaker pins from memory.

**Surprising metal effects:** before deploy, soft-reset, or any board act that may make noise, long tones, bright lights, or motion — **clearly state in chat** what will happen and roughly how long. Not always a new yes/no gate; always a forewarning. Never silent-deploy a screaming boot riff.

Portable manners gaps: file on **tig/bedside**; metal spine gaps: **tig/silico**.

## Definition of done

| Claim | Proof |
|-------|--------|
| `firmware/` change done | `pytest -q` green (host gate). CI green if remote exists. |
| Deployed | `silico deploy … --port COMx --yes --verify` after operator confirmed identity + write. |
| On the metal (first ship) | Deployed **and** operator sees/hears documented **product face** for this GCU (not only version string). |
| Issue fixed | CI green **and** metal matches the issue. |

Never treat "I flashed something" as done. Never claim on-the-metal while the product face is unproven.

## Host gate

```text
python -m pytest -q
silico gate           # deploy-set host-importable; only [hal].allow_machine may import machine
silico product-path   # sim must exercise firmware/defaults.py, not only injects
```

## HAL seam (do not reinvent)

Silico owns the shape that makes the host gate meaningful:

| Path | Role |
|------|------|
| `firmware/hal.py` | Contract only — no `machine` |
| `firmware/hal_board.py` | Device backend — only module allowlisted for `machine` |
| `sim/hal_double.py` | Host double with the same method names |
| `firmware/main.py` | `init(hal=…)` / `tick` — host-import safe; boots only as `__main__` |

Domain modules must not import `machine`. Extend the HAL with product reads/writes; keep the split.

## Serial lifecycle door (hardened consoles)

If your GCU's spec requires hostile-input robustness (Ctrl-C treated as data,
`except BaseException` around the loop), the board becomes unreachable by
mpremote/silico while the app runs. **Any GCU that hardens its console MUST
ship a lifecycle door**: a `repl` protocol verb (park/coast every actuator,
restore the interrupt character, exit cleanly to the interpreter) and a
`reboot` verb (park/coast, then hard reset). Silico's host verbs knock with
`repl\n` automatically when raw-REPL entry fails — but only if your app
answers.

Boot-window warning: after `deploy --reset`, the interrupt char stays enabled
until the app's init runs, so a deploy's own `--verify` can succeed against a
build that is unreachable afterward. Verify-after-reset is not proof of
reachability; the door is. (tig/silico#49, found the hard way on a bench
board that needed a physical replug.)

**Order matters (#62):** do not call `kbd_intr(-1)` until host→device
**round-trip** works and `repl` re-opens mpremote. TX/telem alone is not
duplex. If locked out: recover **once** (stock MicroPython), do not thrash
deploy — see silico `knowledge/esp32-usb-serial.md`.

## Product path

Shipped gains/setpoints/timings live in `firmware/defaults.py` and are what the board runs. At least one sim test must import that module and drive `init`/`tick` (or the control law) with those values. Test-local gains that only work on a synthetic plant are not vehicle-tuned gains — see silico AGENTS **Product path**.

The two rules meet in `firmware/hal_board.py`: it is the one module that may touch `machine`, and it takes its pin numbers from `defaults.py` rather than carrying its own. A shipped value with two copies has two values.

## Layout

| Path | Role |
|------|------|
| `firmware/` | On-device application only (`defaults.py` = shipped params) |
| `sim/` | Host tests; never deploy |
| `scripts/` | Thin wrappers around silico CLI |
| `install/` | End-customer update docs |
| `silico.toml` | Product config (`[deploy].core`, `[hal].allow_machine`, `[host].product_defaults`) |
