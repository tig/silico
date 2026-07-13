"""Argparse adapter for Bedside commands.

Command logic lives in bedside.commands.* so a future tui-cs/cli front-end
can call the same run_* functions without reimplementing behavior.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bedside import __version__
from bedside.commands.doctor_cmd import run_doctor
from bedside.commands.eval_cmd import run_eval
from bedside.commands.init_cmd import run_init
from bedside.exit_codes import SETUP_ERROR
from bedside.result import CommandResult


def _print_result(result: CommandResult) -> int:
    for line in result.messages:
        print(line)
    return result.exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bedside",
        description=(
            "Bedside CLI: pin operator manners, check adoption, eval fixtures. "
            "Minimal Python front-end; command cores are UI-agnostic for a future tui-cs/cli."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"bedside {__version__}",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="project root (default: cwd)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="write bedside.toml, domain notes, AGENTS stub")
    p_init.add_argument("--pin", default="main", help="recorded pin tag or SHA")
    p_init.add_argument(
        "--contract-path",
        default="third_party/bedside/contract",
        help="path to contract dir relative to project root",
    )
    p_init.add_argument("--force", action="store_true", help="overwrite existing config/section")
    p_init.add_argument("--skip-agents", action="store_true", help="do not write AGENTS.md")
    p_init.add_argument(
        "--skip-domain-notes",
        action="store_true",
        help="do not write BEDSIDE.md",
    )

    p_doctor = sub.add_parser("doctor", help="check Bedside adoption health")
    p_doctor.add_argument(
        "--allow-missing-contract",
        action="store_true",
        help="do not fail if contract path is missing (soft check)",
    )

    p_eval = sub.add_parser("eval", help="score fixture(s) against rubric R1-R9")
    p_eval.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="fixture dir(s) or tree; default: configured or packaged eval/fixtures",
    )
    p_eval.add_argument(
        "--json",
        action="store_true",
        dest="json_out",
        help="print machine-readable report",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else SETUP_ERROR
        return code

    root: Path = args.root

    if args.command == "init":
        return _print_result(
            run_init(
                root,
                pin=args.pin,
                contract_path=args.contract_path,
                force=args.force,
                skip_agents=args.skip_agents,
                skip_domain_notes=args.skip_domain_notes,
            )
        )
    if args.command == "doctor":
        return _print_result(
            run_doctor(root, require_contract=not args.allow_missing_contract)
        )
    if args.command == "eval":
        return _print_result(
            run_eval(root, list(args.paths), json_out=args.json_out)
        )

    parser.error(f"unknown command: {args.command}")
    return SETUP_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
