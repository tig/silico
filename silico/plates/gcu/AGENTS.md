# AGENTS.md - GCU product

Guidance for AI coding agents in **this product repo**.

## Spine

Host path comes from **silico** (https://github.com/tig/silico). Pin as host-only. Device `firmware/` never imports silico.

Start: *See https://github.com/tig/silico. Follow the getting started instructions for agents.*

## Help the operator

Assume low ops literacy. Prefer doing over dumping shell. **Poll USB** after asking for a data cable - do not ask humans to announce plug-in. **Never write the device without explicit operator confirmation.**

## Definition of done

| Claim | Proof |
|-------|--------|
| `firmware/` change done | `pytest -q` green (host gate). CI green if remote exists. |
| Deployed | `silico deploy … --yes --verify` after operator confirmed. |
| Issue fixed | CI green **and** metal matches the issue. |

Never treat "I flashed something" as done.

## Host gate

```text
python -m pytest -q
```

## Layout

| Path | Role |
|------|------|
| `firmware/` | On-device application only |
| `sim/` | Host tests; never deploy |
| `scripts/` | Thin wrappers around silico CLI |
| `install/` | End-customer update docs |
| `silico.toml` | Product config |
