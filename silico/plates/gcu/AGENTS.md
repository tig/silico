# AGENTS.md - GCU product

Guidance for AI coding agents in **this product repo**.

## Spine

Host path comes from **silico** (https://github.com/tig/silico). Pin as host-only. Device `firmware/` never imports silico.

Start: *See https://github.com/tig/silico. Follow the getting started instructions for agents.*

That playbook begins with **Phase 0** (welcome the operator, recap what you know, name the next step, get a clear go) **before** any tooling. Operator manners follow **Bedside** (pinned in silico; see silico `BEDSIDE.md` / vendored contract).

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
```

## Layout

| Path | Role |
|------|------|
| `firmware/` | On-device application only |
| `sim/` | Host tests; never deploy |
| `scripts/` | Thin wrappers around silico CLI |
| `install/` | End-customer update docs |
| `silico.toml` | Product config |
