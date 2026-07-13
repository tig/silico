# BEDSIDE.md (silico domain notes only)

This file is **not** a fork of the Bedside principles.

Normative rules: `third_party/bedside/contract` (vendored from https://github.com/tig/bedside).
Pin: see `bedside.toml`.

## Operator persona

Smart, high-judgment (product / hardware / field). Often low literacy in Git, pip, COM ports, UF2, agent UIs. Own judgment and metal confirmation. Do not examine or shame them.

## First-run from zero

1. Machine: Git, Python 3.11+, `gh`, pip (`silico` host package).
2. `pip install -e ".[dev]"` and `pip install -e ./third_party/bedside` (or CI equivalent).
3. `silico doctor` then GCU pin/scaffold/pytest (Day 1 playbook in AGENTS.md).
4. First MicroPython / UF2 on the board once; then app updates only.

## Scary surfaces (plain language)

- **USB serial:** list ports with scores; prefer explicit `COMx`; demote CH340 and Debug Probe.
- **Multi-device hosts:** never blind `connect auto`.
- **Deploy:** inspect first; never write without operator yes (`silico deploy … --yes`).
- **USB wait:** if you say you are polling, actually run a long `silico wait-device`; do not ask them to announce plug-in.
- **Board identity:** high score is a hint; confirm product board before deploy.

## Day-2 leave-behind

One update path (GCU install docs), typically:

```text
pytest -q
silico deploy firmware/… --port COMx --yes --verify
```

What good looks like: host gate green; device `FW_VERSION` matches host; documented LED/status pattern.

## Improve Bedside (customer 0)

When silico use finds gaps in contract, surface patterns, CLI, eval heuristics, or fixtures:

1. Prefer fixing silico domain notes / silico CLI when the gap is metal-specific.
2. Prefer **filing an issue on `tig/bedside`** when the gap is portable operator manners.
3. Do not soft-fork the nine principles into a kinder local copy.

```text
gh issue create -R tig/bedside --title "…" --body "…"
```
