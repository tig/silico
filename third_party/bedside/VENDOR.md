# Vendored tig/bedside

- Source: https://github.com/tig/bedside
- Tag / commit: **v0.2.0** / `c4c0381d4d4e0c9c378fca992c673de2f6c3df64` (c4c0381)
- Vendored: not a git submodule (copy for pin/reproducible host path)
- Refresh: replace this tree from a new bedside commit; update this file and root `bedside.toml` pin

## Local overlay (silico#84 / silico#89)

Upstream `ask` still exits **10** on any non-recommended choice (`OK if matched else HUMAN_NEEDED`). Silico carries a local behavior change so **any valid choice exits 0**; agents branch on `choice=` / `matched_recommended`, and halt only on the safe decline for that gate.

Touched after each re-vendor:

- `src/bedside/commands/ask_cmd.py`
- `src/bedside/exit_codes.py` (module docstring)
- `tests/test_ask_step.py` (scary-yes / alternate-fork expectations)
- Exit-code prose in `README.md`, `AGENTS.md`, `surface/README.md`, and
  `eval/fixtures/known-good/operator-gate-ask/transcript.md` (keep docs matching the overlay)

Root `bedside.toml` pin note: `silico-local-ask-explicit-yes-0`.

**Preferred next step (issue #89):** land the same exit-code semantics on **tig/bedside** so consumers do not keep two definitions of exit 10. Keep re-applying this overlay until that lands.

## Improve upstream

When silico hits gaps, bugs, or missing surface/eval in Bedside, **file issues on tig/bedside** (customer 0). Do not silently soft-fork tenets in silico AGENTS.md.
