"""bedside init: write project pin config and AGENTS stub."""

from __future__ import annotations

import re
from pathlib import Path

from bedside.config import BedsideConfig, config_path, write_config
from bedside.exit_codes import OK, SETUP_ERROR
from bedside.result import CommandResult
from bedside.vendor import detect_pin, vendor_copy

AGENTS_SECTION = """## Help the operator (Bedside)

We follow [Bedside](https://github.com/tig/bedside): manners for agents
operating tools for smart, high-judgment non-experts.

- Pin: see `bedside.toml` (do not soft-fork principles).
- Normative contract path: `{contract_path}`
- Human gates: call `bedside ask` / `bedside step` (or the host structured
  choice UI). Do not restate multi-choice free-text walls in this file.

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
    vendor_from: Path | None = None,
    vendor_dest: str = "third_party/bedside",
    include_src: bool = True,
    domain_fixtures: str = "eval/fixtures",
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
        r.line(
            "What to do next: use `--force` to overwrite config, or edit bedside.toml. "
            "To re-vendor only: `bedside init --vendor-from <path> --force`."
        )
        return r

    r = CommandResult(OK)
    effective_contract = contract_path.replace("\\", "/")
    effective_pin = pin

    if vendor_from is not None:
        src = vendor_from if vendor_from.is_absolute() else (root / vendor_from)
        src = src.resolve()
        dest = (root / vendor_dest).resolve()
        try:
            copied = vendor_copy(src, dest, include_src=include_src)
        except (OSError, FileNotFoundError) as e:
            bad = CommandResult(SETUP_ERROR)
            bad.line(f"Vendor copy failed: {e}")
            bad.line(
                "What to do next: pass a local tig/bedside checkout to "
                "`--vendor-from` (must contain contract/)."
            )
            return bad
        detected = detect_pin(src)
        if pin == "main" and detected:
            effective_pin = detected
        effective_contract = f"{vendor_dest.rstrip('/')}/contract"
        r.line(f"Vendored Bedside into {vendor_dest}/ ({', '.join(copied)})")
        r.line(f"VENDOR.md pin stamp: {detected or 'unknown'}")

    contract = Path(effective_contract)
    contract_s = (
        contract.as_posix() if contract.is_absolute() else effective_contract.replace("\\", "/")
    )
    parent = contract.parent
    surface_s = (parent / "surface").as_posix()
    eval_s = (parent / "eval").as_posix()

    # Domain fixtures outside the vendor tree so refresh does not wipe them.
    domain = domain_fixtures.replace("\\", "/")
    fixture_paths = [f"{eval_s}/fixtures"]
    if domain and domain not in fixture_paths:
        fixture_paths.append(domain)

    cfg = BedsideConfig(
        pin=effective_pin,
        contract_path=contract_s,
        surface_path=surface_s,
        eval_path=eval_s,
        fixture_paths=fixture_paths,
    )
    write_config(root, cfg)
    try:
        shown = str(cfg_file.relative_to(root))
    except ValueError:
        shown = str(cfg_file)
    r.line(f"Wrote {shown}")

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

    if domain:
        domain_dir = root / domain
        (domain_dir / "known-bad").mkdir(parents=True, exist_ok=True)
        (domain_dir / "known-good").mkdir(parents=True, exist_ok=True)
        readme = domain_dir / "README.md"
        if not readme.is_file() or force:
            readme.write_text(
                "# Domain fixtures\n\n"
                "Product-specific Bedside transcripts live here.\n\n"
                "They are **outside** `third_party/bedside` so re-vendor does not delete them.\n\n"
                "Layout: `known-bad/<id>/{meta.toml,transcript.md}` and "
                "`known-good/<id>/...` (same shape as upstream `eval/fixtures`).\n\n"
                "Run: `bedside eval` (uses `fixture_paths` in bedside.toml) or "
                "`bedside eval third_party/bedside/eval/fixtures eval/fixtures`.\n",
                encoding="utf-8",
            )
        r.line(f"Scaffolded domain fixture dirs under {domain}/")

    r.line("")
    r.line(f"Pin recorded as: {cfg.pin}")
    r.line(f"Contract path: {cfg.contract_path}")
    r.line(f"Fixture paths: {', '.join(cfg.fixture_paths)}")
    r.line("What to do next:")
    if vendor_from is None:
        r.line("  1. Put Bedside on disk (vendor-copy recommended; submodule also fine):")
        r.line("     bedside init --vendor-from /path/to/tig/bedside --force")
        r.line("     Docs: docs/adopting.md")
    else:
        r.line("  1. Contract tree is under the vendor dest (see VENDOR.md there).")
    r.line("  2. Fill domain notes in BEDSIDE.md (first-run, scary surfaces, Day-2).")
    r.line("  3. Add domain fixtures under eval/fixtures (never under third_party/).")
    r.line("  4. Run `bedside doctor` then `bedside eval`.")
    return r
