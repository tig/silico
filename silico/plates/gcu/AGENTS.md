# AGENTS.md - GCU product

Guidance for AI coding agents in **this product repo**.

## Spine

Host path comes from **silico** (https://github.com/tig/silico). Pin as host-only. Device `firmware/` never imports silico.

Start: *See https://github.com/tig/silico. Follow the getting started instructions for agents.*

That playbook begins with **Phase 0** (welcome the operator, recap what you know, name the next step, get a clear go) **before** any tooling. Operator manners follow **Bedside** (pinned in silico; see silico `BEDSIDE.md` / vendored contract).

Day 1 is **host gate + device USB talk/prep**, not host-only. After scaffold and green pytest, continue into `wait-device` / `inspect` / REPL (or UF2) unless the operator explicitly defers metal.

## Help the operator

Assume low ops literacy. Prefer doing over dumping shell. **Poll USB** after asking for a data cable - do not ask humans to announce plug-in. **Confirm device identity** every session. **Never write the device without explicit operator confirmation.** Portable manners gaps: file on **tig/bedside**; metal spine gaps: **tig/silico**.

## Definition of done

| Claim | Proof |
|-------|--------|
| `firmware/` change done | `pytest -q` green (host gate). CI green if remote exists. |
| Deployed | `silico deploy … --port COMx --yes --verify` after operator confirmed identity + write. |
| Issue fixed | CI green **and** metal matches the issue. |

Never treat "I flashed something" as done.

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
