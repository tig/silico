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
silico gate   # deploy-set host-importable; only [hal].allow_machine may import machine
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

## Layout

| Path | Role |
|------|------|
| `firmware/` | On-device application only |
| `sim/` | Host tests; never deploy |
| `scripts/` | Thin wrappers around silico CLI |
| `install/` | End-customer update docs |
| `silico.toml` | Product config (`[deploy].core`, `[hal].allow_machine`) |
