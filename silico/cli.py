"""Agent-first CLI: thin verbs, clear exit codes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from silico import __version__
from silico.deploy import DeployResult, deploy, plan_deploy
from silico.doctor import run_doctor
from silico.inspect_device import inspect
from silico.scaffold import scaffold
from silico.wait_device import wait_for_board


def _print_lines(lines: list[str]) -> None:
    for line in lines:
        print(line)


def cmd_doctor(_args: argparse.Namespace) -> int:
    report = run_doctor()
    _print_lines(report.lines)
    return 0 if report.ok else 1


def cmd_wait_device(args: argparse.Namespace) -> int:
    print(
        f"Polling USB for a preferred board (score>=50) up to {args.timeout}s. "
        "Do not ask the human to announce plug-in - only ask them to use a data cable if needed."
    )
    port = wait_for_board(timeout_s=args.timeout, poll_s=args.poll)
    if port is None:
        print("TIMEOUT: no preferred board appeared.")
        print("Try: data USB cable (not charge-only), different port, hold BOOT+RESET for RPI-RP2 UF2 path.")
        return 1
    print(f"OK: {port.device} - {port.label}")
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    report = inspect(port=args.port)
    _print_lines(report.lines)
    return 0 if report.ok else 1


def cmd_deploy(args: argparse.Namespace) -> int:
    files = [Path(f) for f in args.files]
    if not args.yes:
        planned = plan_deploy(files, port=args.port)
        _print_lines(planned.lines)
        if isinstance(planned, DeployResult):
            return 1
        print("Dry plan only. Re-run with --yes after explicit operator confirmation.")
        return 2  # needs confirmation

    result = deploy(
        files,
        port=args.port,
        yes=True,
        verify=args.verify,
        expect_name=args.expect_name,
        expect_version=args.expect_version,
        reset=args.reset,
    )
    _print_lines(result.lines)
    return 0 if result.ok else 1


def cmd_scaffold(args: argparse.Namespace) -> int:
    dest = Path(args.path)
    try:
        lines = scaffold(dest, force=args.force)
    except FileExistsError as e:
        print(f"FAIL: {e}")
        return 1
    except FileNotFoundError as e:
        print(f"FAIL: {e}")
        return 1
    _print_lines(lines)
    return 0


def cmd_version(_args: argparse.Namespace) -> int:
    print(__version__)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="silico",
        description="Prompt for metal - host spine for GCUs (agent-first CLI).",
    )
    p.add_argument("--version", action="store_true", help="print version and exit")
    sub = p.add_subparsers(dest="cmd", required=False)

    d = sub.add_parser("doctor", help="host environment + scored serial ports (read-only)")
    d.set_defaults(func=cmd_doctor)

    w = sub.add_parser("wait-device", help="poll USB until preferred board appears")
    w.add_argument("--timeout", type=float, default=60.0)
    w.add_argument("--poll", type=float, default=1.0)
    w.set_defaults(func=cmd_wait_device)

    i = sub.add_parser("inspect", help="non-destructive device inspect (no writes)")
    i.add_argument("--port", default=None, help="explicit COMx / device path")
    i.set_defaults(func=cmd_inspect)

    dep = sub.add_parser(
        "deploy",
        help="copy files to device; requires --yes after operator confirmation",
    )
    dep.add_argument("files", nargs="+", help="local files to copy (basename = remote name)")
    dep.add_argument("--port", default=None)
    dep.add_argument(
        "--yes",
        action="store_true",
        help="operator explicitly confirmed overwrite (required to write)",
    )
    dep.add_argument("--verify", action="store_true", help="import version on device after write")
    dep.add_argument("--expect-name", default=None)
    dep.add_argument("--expect-version", default=None)
    dep.add_argument("--reset", action="store_true", help="soft reset after deploy")
    dep.set_defaults(func=cmd_deploy)

    s = sub.add_parser("scaffold", help="create GCU plate from versioned template")
    s.add_argument("path", nargs="?", default=".", help="destination directory (default: .)")
    s.add_argument(
        "--force",
        action="store_true",
        help="allow writing into non-empty directory (skip existing files still unless overwritten)",
    )
    s.set_defaults(func=cmd_scaffold)

    v = sub.add_parser("version", help="print package version")
    v.set_defaults(func=cmd_version)

    return p


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    if not argv:
        parser.print_help()
        return 0
    # allow `silico --version`
    if argv == ["--version"] or (len(argv) == 1 and argv[0] in ("-V",)):
        print(__version__)
        return 0
    args = parser.parse_args(argv)
    if getattr(args, "version", False) and not getattr(args, "cmd", None):
        print(__version__)
        return 0
    if not getattr(args, "cmd", None):
        parser.print_help()
        return 0
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
