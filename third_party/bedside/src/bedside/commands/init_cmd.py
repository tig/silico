"""bedside init: write project pin config and AGENTS stub."""

from __future__ import annotations

from pathlib import Path

from bedside.config import BedsideConfig, config_path, write_config
from bedside.exit_codes import OK, SETUP_ERROR
from bedside.result import CommandResult

AGENTS_SECTION = """## Help the operator (Bedside)

We follow [Bedside](https://github.com/tig/bedside): manners for agents
operating tools for smart, high-judgment non-experts.

- Pin: see `bedside.toml` (do not soft-fork principles).
- Normative contract path: `{contract_path}`

Summary (full contract is normative):

1. Assume low ops literacy, high judgment.
2. No wall of unexplained shell.
3. Prefer doing over instructing.
4. Human acts: explicit, one step, dumb-simple.
5. Own first-time setup from zero.
6. Own scary surfaces in plain language.
7. Confirm in their words before irreversible or physical steps.
8. Never leave them at a cliff.
9. Teach only what Day 2 requires.

### Domain notes (this repo only)

- First-run: <!-- describe from-zero path -->
- Scary surfaces: <!-- ports, auth, permissions -->
- Day-2 leave-behind: <!-- one command; what good looks like -->
"""

BEDSIDE_MD = """# BEDSIDE.md (domain notes only)

This file is **not** a fork of the Bedside principles.

Pin and paths: see `bedside.toml`. Normative rules live at the contract path.

## Domain notes

- Operator persona: smart, high-judgment; low ops literacy in our tools.
- First-run from zero:
- Scary surfaces (plain language):
- Day-2 leave-behind (one path + what good looks like):
"""


def run_init(
    root: Path,
    *,
    pin: str = "main",
    contract_path: str = "third_party/bedside/contract",
    force: bool = False,
    skip_agents: bool = False,
    skip_domain_notes: bool = False,
) -> CommandResult:
    root = root.resolve()
    if not root.is_dir():
        r = CommandResult(SETUP_ERROR)
        r.line(f"Not a directory: {root}")
        r.line("What to do next: pass an existing project directory to `bedside init`.")
        return r

    cfg_file = config_path(root)
    if cfg_file.is_file() and not force:
        r = CommandResult(SETUP_ERROR)
        r.line(f"Already initialized: {cfg_file}")
        r.line("What to do next: use `--force` to overwrite config, or edit bedside.toml.")
        return r

    contract = Path(contract_path)
    # Prefer portable path strings in bedside.toml (forward slashes).
    contract_s = contract.as_posix() if contract.is_absolute() else contract_path.replace("\\", "/")
    parent = contract.parent
    surface_s = (parent / "surface").as_posix() if contract.is_absolute() else (parent / "surface").as_posix()
    eval_s = (parent / "eval").as_posix() if contract.is_absolute() else (parent / "eval").as_posix()
    cfg = BedsideConfig(
        pin=pin,
        contract_path=contract_s,
        surface_path=surface_s,
        eval_path=eval_s,
    )
    write_config(root, cfg)
    r = CommandResult(OK)
    r.line(f"Wrote {cfg_file.relative_to(root)}")

    if not skip_domain_notes:
        notes = root / cfg.domain_notes
        if notes.is_file() and not force:
            r.line(f"Left existing {cfg.domain_notes}")
        else:
            notes.write_text(BEDSIDE_MD, encoding="utf-8")
            r.line(f"Wrote {cfg.domain_notes}")

    if not skip_agents:
        agents = root / "AGENTS.md"
        section = AGENTS_SECTION.format(contract_path=cfg.contract_path)
        if agents.is_file():
            text = agents.read_text(encoding="utf-8")
            if "Help the operator (Bedside)" in text and not force:
                r.line("AGENTS.md already has a Bedside section; left unchanged.")
            elif "Help the operator (Bedside)" in text and force:
                # replace section roughly from heading to next ## or EOF
                import re

                new_text, n = re.subn(
                    r"## Help the operator \(Bedside\).*?(?=\n## |\Z)",
                    section.rstrip() + "\n\n",
                    text,
                    count=1,
                    flags=re.S,
                )
                if n:
                    agents.write_text(new_text, encoding="utf-8")
                    r.line("Replaced Bedside section in AGENTS.md")
                else:
                    agents.write_text(text.rstrip() + "\n\n" + section, encoding="utf-8")
                    r.line("Appended Bedside section to AGENTS.md")
            else:
                agents.write_text(text.rstrip() + "\n\n" + section, encoding="utf-8")
                r.line("Appended Bedside section to AGENTS.md")
        else:
            agents.write_text(
                "# AGENTS.md\n\n"
                "Project guidance for AI coding agents.\n\n" + section,
                encoding="utf-8",
            )
            r.line("Wrote AGENTS.md with Bedside section")

    r.line("")
    r.line(f"Pin recorded as: {cfg.pin}")
    r.line(f"Contract path: {cfg.contract_path}")
    r.line("What to do next:")
    r.line("  1. Vendor or submodule tig/bedside so the contract path exists on disk.")
    r.line("  2. Fill domain notes in BEDSIDE.md (first-run, scary surfaces, Day-2).")
    r.line("  3. Run `bedside doctor` then `bedside eval` on your fixtures.")
    return r
