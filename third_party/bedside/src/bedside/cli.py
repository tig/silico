"""Argparse adapter for Bedside commands.

Command logic lives in bedside.commands.* so a future tui-cs/cli front-end
can call the same run_* functions without reimplementing behavior.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bedside import __version__
from bedside.commands.ask_cmd import parse_choices, run_ask
from bedside.commands.doctor_cmd import run_doctor
from bedside.commands.eval_cmd import run_eval
from bedside.commands.init_cmd import run_init
from bedside.commands.step_cmd import run_step
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
            "Bedside CLI: pin operator manners, check adoption, eval fixtures, "
            "operator gates (ask/step). Minimal Python front-end; command cores "
            "are UI-agnostic for a future tui-cs/cli."
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

    p_init = sub.add_parser(
        "init",
        help="write bedside.toml, domain notes, AGENTS stub; optional vendor-copy",
    )
    p_init.add_argument(
        "--pin",
        default="main",
        help="recorded pin tag or SHA (default: main; with --vendor-from, git HEAD if main)",
    )
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
    p_init.add_argument(
        "--vendor-from",
        type=Path,
        default=None,
        help="local tig/bedside checkout to copy into --vendor-dest (no submodule)",
    )
    p_init.add_argument(
        "--vendor-dest",
        default="third_party/bedside",
        help="destination for vendor-copy (default: third_party/bedside)",
    )
    p_init.add_argument(
        "--no-src",
        action="store_true",
        help="with --vendor-from, skip copying src/ (docs/fixtures only)",
    )
    p_init.add_argument(
        "--domain-fixtures",
        default="eval/fixtures",
        help="product fixture root outside vendor tree (default: eval/fixtures)",
    )

    p_doctor = sub.add_parser("doctor", help="check Bedside adoption health")
    p_doctor.add_argument(
        "--allow-missing-contract",
        action="store_true",
        help="do not fail if contract path is missing (soft check)",
    )

    p_eval = sub.add_parser(
        "eval",
        help="score fixture dir(s) against rubric R1-R9 (multi-root OK)",
    )
    p_eval.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help=(
            "fixture dir(s) or trees; default: fixture_paths from bedside.toml "
            "(vendored + domain)"
        ),
    )
    p_eval.add_argument(
        "--json",
        action="store_true",
        dest="json_out",
        help="print machine-readable report",
    )

    p_ask = sub.add_parser(
        "ask",
        help="one structured operator choice (yes/no or multi-choice gate)",
    )
    p_ask.add_argument(
        "--id",
        required=True,
        dest="gate_id",
        help="stable gate id for logs and eval",
    )
    p_ask.add_argument(
        "--prompt",
        required=True,
        help="plain-language question for the operator",
    )
    p_ask.add_argument(
        "--choices",
        default="yes,no",
        help="comma-separated choices (default: yes,no)",
    )
    p_ask.add_argument(
        "--default",
        default=None,
        help="recommended choice (default: first choice); shown first",
    )
    p_ask.add_argument(
        "--answer",
        default=None,
        help="non-interactive answer (label or 1-based index)",
    )
    p_ask.add_argument(
        "--json",
        action="store_true",
        dest="json_out",
        help="print machine-readable result",
    )

    p_step = sub.add_parser(
        "step",
        help="one human body/browser act, then confirm in their words",
    )
    p_step.add_argument(
        "--id",
        required=True,
        dest="gate_id",
        help="stable step id for logs and eval",
    )
    p_step.add_argument(
        "--prompt",
        required=True,
        help="one physical or browser instruction",
    )
    p_step.add_argument(
        "--expect",
        default=None,
        help="what the operator should be able to say when done (their words)",
    )
    p_step.add_argument(
        "--confirm",
        action="store_true",
        help="non-interactive: mark step confirmed",
    )
    p_step.add_argument(
        "--decline",
        action="store_true",
        help="non-interactive: mark step not confirmed",
    )
    p_step.add_argument(
        "--no-wait",
        action="store_true",
        help="show the step only; exit 10 (human still needed)",
    )
    p_step.add_argument(
        "--json",
        action="store_true",
        dest="json_out",
        help="print machine-readable result",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        # argparse: 0 for --help/--version; 2 for usage errors. Agents branch on
        # 10 vs 30, so map usage errors to SETUP_ERROR (not bare 2).
        if e.code in (0, None):
            return 0
        return SETUP_ERROR

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
                vendor_from=args.vendor_from,
                vendor_dest=args.vendor_dest,
                include_src=not args.no_src,
                domain_fixtures=args.domain_fixtures,
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
    if args.command == "ask":
        return _print_result(
            run_ask(
                gate_id=args.gate_id,
                prompt=args.prompt,
                choices=parse_choices(args.choices),
                default=args.default,
                answer=args.answer,
                json_out=args.json_out,
            )
        )
    if args.command == "step":
        if args.confirm and args.decline:
            r = CommandResult(SETUP_ERROR)
            r.line("step: use only one of --confirm or --decline.")
            r.line("What to do next: pick one flag, or omit both for interactive.")
            return _print_result(r)
        confirm: bool | None
        if args.confirm:
            confirm = True
        elif args.decline:
            confirm = False
        else:
            confirm = None
        return _print_result(
            run_step(
                gate_id=args.gate_id,
                prompt=args.prompt,
                expect=args.expect,
                confirm=confirm,
                wait_confirm=not args.no_wait,
                json_out=args.json_out,
            )
        )

    parser.error(f"unknown command: {args.command}")
    return SETUP_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
