# BEDSIDE.md (domain notes only)

This file is **not** a fork of the Bedside principles.

Pin and paths: see `bedside.toml`. Normative rules live at `contract/`.

## Domain notes

- Operator persona: smart, high-judgment; may not know Python packaging or pytest.
- First-run from zero: install Python 3.11+, `pip install -e ".[dev]"`, run `bedside doctor`, run `bedside eval`.
- Scary surfaces: none for metal; explain venv only if install fails.
- Day-2 leave-behind: `pytest -q` and `bedside eval` (what good looks like: all fixtures OK).
