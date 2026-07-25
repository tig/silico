# AGENTS.md

Project guidance for AI coding agents working in **tig/bedside**.

## What this repo is

Portable Bedside standard: `contract/`, `surface/`, `eval/`, plus a minimal Python CLI (`src/bedside/`). Not silico. Not mcec. Not domain product UX.

Human index: [README.md](README.md). Writing style: follow Tig voice mechanics (no em-dashes, no horizontal rules, short paragraphs, Oxford commas, sentence-ended list items) when editing prose.

Brand images: [docs/images/README.md](docs/images/README.md). Canonical `docs/images/hero.jpg` (README) and `docs/images/social-preview.jpg` (GitHub 1280×640). Export social with `python scripts/export_social_preview.py`.

## Help the operator (Bedside)

We follow [Bedside](https://github.com/tig/bedside): manners for agents
operating tools for smart, high-judgment non-experts.

- Pin: see `bedside.toml` (do not soft-fork tenets).
- Normative contract path: `contract`
- Human gates: call `bedside ask` / `bedside step` (or the host structured choice UI).

Summary (full contract is normative):

1. Assume low ops literacy, high judgment.
2. No walls of shell or choice.
3. Prefer doing over instructing.
4. No silent work.
5. Human acts are explicit and dumb-simple.
6. Own first-time setup from zero.
7. Own scary surfaces in plain language.
8. Confirm what they can see, in their words.
9. Never leave them at a cliff.
10. Teach only what tomorrow requires.
11. Compound what you learn.

### Domain notes (this repo only)

- First-run: `pip install -e ".[dev]"` then `bedside doctor` and `bedside eval`.
- Scary surfaces: none physical; prefer doing install and tests yourself.
- Leave-behind: `pytest -q` and `bedside eval` (one proof path for manners).

## CLI architecture

- `bedside.cli`: argparse adapter only.
- `bedside.commands.*`: UI-agnostic command cores (future tui-cs/cli should call these).
- `bedside.eval_engine`: rule-based R1-R11 scoring.
- Operator gates: `ask` (structured choice) and `step` (one human act + confirm).
- Exit codes (silico#84 overlay): 0 any valid ask choice or confirmed step; 10 still needed / step declined; 20 manners fail; 30 setup error. Branch ask on `choice=` / `matched_recommended`, not on exit 0 alone.

## Definition of done

| Claim | Proof |
|-------|--------|
| CLI or eval change | `pytest -q` green |
| Fixture change | `bedside eval` green (expects still match) |
| Prose change | no em-dashes; list items are sentences |
