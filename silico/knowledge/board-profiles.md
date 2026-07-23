# Board profiles (Day-1 product-face pin packs)

**Not product domain.** Packaged GPIO / face candidates for common boards so agents do not invent pin maps from chat folklore.

Normative tools: `silico board-profile`, `parts.toml` `profile = "…"`, `silico board-profile seed`.

## Why

Day-1 metal needs an operator-observable **product face** (see root AGENTS Phase D1). On M5GO-class units that often means **side strip + speaker**, not a random module LED. Pin numbers used to live only in knowledge notes (`esp32-audio.md`, bench lore). Prefer a **board profile** that agents can list and seed into `firmware/defaults.py` as **candidates**.

## Workflow

1. Identify the board (operator / docs / `parts.toml`).
2. Link profile on the board part:

```toml
[[part]]
id = "m5go"
name = "M5GO IoT Kit"
role = "board"
profile = "m5go"
docs = "https://docs.m5stack.com/en/core/m5go"
```

3. Inspect candidates:

```text
silico board-profile
silico board-profile show m5go
silico parts   # also reports linked profile
```

4. Dry-run seed into shipped defaults, then write after operator confirm:

```text
silico board-profile seed m5go          # dry-run
silico board-profile seed m5go --yes    # writes firmware/defaults.py
```

5. Host gate → confirmed deploy → operator **see/hear** product face. Profile seed alone is **not** metal done.

## Packaged profiles

| Id | Face candidates (summary) |
|----|---------------------------|
| `m5go` | LED/side strip **15**, speaker **25** |
| `xiao-rp2040` | User LED **16** (plate default) |

Add a new `silico/boards/<id>.toml` when a common board is proven on bench. Keep `defaults_candidates` keys aligned with product `defaults.py` names.

## Anti-patterns

- Hard-code GPIO15/25 in agent chat only; leave no profile for the next agent.
- Seed with `--yes` without operator board confirmation.
- Claim Day-1 metal done because defaults match a profile (still need observe).
- Soft-fork board pin tables into each GCU without promoting a silico profile when reusable.
