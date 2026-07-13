"""bedside doctor: adoption health in plain language."""

from __future__ import annotations

from pathlib import Path

from bedside.config import load_config, repo_root_from_package, resolve_under
from bedside.exit_codes import MANNERS_FAIL, OK, SETUP_ERROR
from bedside.result import CommandResult


def run_doctor(root: Path, *, require_contract: bool = True) -> CommandResult:
    root = root.resolve()
    checks: list[tuple[str, bool, str]] = []

    cfg = load_config(root)
    if cfg is None:
        checks.append(
            (
                "bedside.toml",
                False,
                "missing; run `bedside init` in the project root",
            )
        )
        r = CommandResult(SETUP_ERROR)
        r.line("Bedside doctor: not initialized")
        for name, ok, detail in checks:
            mark = "OK" if ok else "FAIL"
            r.line(f"  [{mark}] {name}: {detail}")
        r.line("What to do next: `bedside init` then vendor tig/bedside at the pin.")
        return r

    checks.append(("bedside.toml", True, f"pin={cfg.pin}"))

    contract = resolve_under(root, cfg.contract_path)
    contract_ok = contract.is_dir() and (contract / "README.md").is_file()
    if not contract_ok:
        # Developing inside tig/bedside itself
        pkg_contract = repo_root_from_package() / "contract"
        if pkg_contract.is_dir() and root.resolve() == repo_root_from_package().resolve():
            contract = pkg_contract
            contract_ok = True
            checks.append(
                (
                    "contract",
                    True,
                    f"using repo contract/ (pin={cfg.pin})",
                )
            )
        else:
            checks.append(
                (
                    "contract",
                    False,
                    f"not found at {cfg.contract_path}; clone/submodule tig/bedside",
                )
            )
    else:
        checks.append(("contract", True, str(contract)))

    agents = root / "AGENTS.md"
    if agents.is_file():
        text = agents.read_text(encoding="utf-8")
        has = "Bedside" in text or "Help the operator" in text
        checks.append(
            (
                "AGENTS.md",
                has,
                "Bedside section present" if has else "no Bedside / Help the operator mention",
            )
        )
    else:
        checks.append(("AGENTS.md", False, "missing"))

    notes = root / cfg.domain_notes
    if notes.is_file():
        body = notes.read_text(encoding="utf-8")
        filled = "<!--" not in body or body.count("<!--") < 3
        # soft: file exists is enough for doctor OK
        checks.append((cfg.domain_notes, True, "present" + ("" if filled else " (still has stubs)")))
    else:
        checks.append((cfg.domain_notes, False, "missing domain notes file"))

    eval_root = resolve_under(root, cfg.eval_path)
    fixtures = eval_root / "fixtures"
    if fixtures.is_dir():
        checks.append(("eval fixtures", True, str(fixtures)))
    else:
        pkg_fix = repo_root_from_package() / "eval" / "fixtures"
        if root.resolve() == repo_root_from_package().resolve() and pkg_fix.is_dir():
            checks.append(("eval fixtures", True, str(pkg_fix)))
        else:
            checks.append(
                (
                    "eval fixtures",
                    False,
                    f"not at {cfg.eval_path}/fixtures (optional until you add domain fixtures)",
                )
            )

    failed_hard = [c for c in checks if not c[1] and c[0] in {"bedside.toml", "AGENTS.md"}]
    failed_contract = [c for c in checks if not c[1] and c[0] == "contract"]

    if failed_hard or (require_contract and failed_contract):
        code = SETUP_ERROR if (not cfg or failed_hard) else MANNERS_FAIL
        # contract missing is setup for adopters
        if failed_contract and require_contract:
            code = SETUP_ERROR
        r = CommandResult(code)
        r.line("Bedside doctor: issues found")
    else:
        soft_fail = [c for c in checks if not c[1]]
        if soft_fail:
            r = CommandResult(OK)
            r.line("Bedside doctor: OK with notes")
        else:
            r = CommandResult(OK)
            r.line("Bedside doctor: OK")

    for name, ok, detail in checks:
        mark = "OK" if ok else "FAIL"
        r.line(f"  [{mark}] {name}: {detail}")

    if r.exit_code != OK:
        r.line("What to do next: fix FAIL items above; re-run `bedside doctor`.")
    else:
        r.line("What to do next: `bedside eval` on known-bad and known-good fixtures.")
    return r
