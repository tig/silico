# AGENTS.md

Project guidance for AI coding agents working in **tig/bedside**.

## What this repo is

Portable Bedside standard: `contract/`, `surface/`, `eval/`, plus a minimal Python CLI (`src/bedside/`). Not silico. Not mcec. Not domain product UX.

Human index: [README.md](README.md). Writing style: follow Tig voice mechanics (no em-dashes, no horizontal rules, short paragraphs, Oxford commas, sentence-ended list items) when editing prose.

## Help the operator (Bedside)

We follow [Bedside](https://github.com/tig/bedside): manners for agents
operating tools for smart, high-judgment non-experts.

- Pin: see `bedside.toml` (do not soft-fork principles).
- Normative contract path: `contract`
- Human gates: call `bedside ask` / `bedside step` (or the host structured choice UI).

Summary (full contract is normative):

1. Assume low ops literacy, high judgment.
2. No wall of unexplained shell (or free-text choice walls).
3. Prefer doing over instructing.
4. Human acts: explicit, one step, dumb-simple.
5. Own first-time setup from zero.
6. Own scary surfaces in plain language.
7. Confirm in their words before irreversible or physical steps.
8. Never leave them at a cliff.
9. Teach only what Day 2 requires.

### Domain notes (this repo only)

- First-run: `pip install -e ".[dev]"` then `bedside doctor` and `bedside eval`.
- Scary surfaces: none physical; prefer doing install and tests yourself.
- Day-2 leave-behind: `pytest -q` and `bedside eval` (one proof path for manners).

## CLI architecture

- `bedside.cli`: argparse adapter only.
- `bedside.commands.*`: UI-agnostic command cores (future tui-cs/cli should call these).
- `bedside.eval_engine`: rule-based R1-R9 scoring.
- Operator gates: `ask` (structured choice) and `step` (one human act + confirm).
- Exit codes: 0 ok, 10 human-needed / non-recommended ask / declined step, 20 manners fail, 30 setup error.

## Definition of done

| Claim | Proof |
|-------|--------|
| CLI or eval change | `pytest -q` green |
| Fixture change | `bedside eval` green (expects still match) |
| Prose change | no em-dashes; list items are sentences |
