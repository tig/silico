"""Agent-first CLI: thin verbs, clear exit codes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from silico import __version__
from silico.deploy import DeployResult, deploy, plan_deploy
from silico.doctor import run_doctor
from silico.inspect_device import inspect
from silico.monitor import monitor_port
from silico.pull_device import pull_device
from silico.scaffold import scaffold
from silico.wait_device import TIMEOUT_SOP, format_port_snapshot, wait_for_board


def _print_lines(lines: list[str]) -> None:
    for line in lines:
        print(line)


def cmd_doctor(_args: argparse.Namespace) -> int:
    report = run_doctor()
    _print_lines(report.lines)
    return 0 if report.ok else 1


def cmd_wait_device(args: argparse.Namespace) -> int:
    print(
        f"Polling USB for a preferred board (score>=50) up to {args.timeout}s "
        f"(poll every {args.poll}s)."
    )
    print(
        "Do not ask the human to announce plug-in - only ask for a data cable / physical plug if needed."
    )
    last_snap = {"text": None}

    def on_poll(elapsed: float, ports) -> None:
        snap = format_port_snapshot(ports)
        if snap != last_snap["text"] or int(elapsed) % 10 == 0:
            print(f"  t={elapsed:5.1f}s  ports: {snap}", flush=True)
            last_snap["text"] = snap

    port = wait_for_board(
        timeout_s=args.timeout,
        poll_s=args.poll,
        on_poll=on_poll,
    )
    if port is None:
        _print_lines(TIMEOUT_SOP)
        return 1
    print(f"OK: {port.device} - {port.label}")
    print(
        "Next: silico inspect --port "
        + port.device
        + " then CONFIRM with operator this is the product board before deploy."
    )
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    report = inspect(
        port=args.port,
        apply_mpy_pin=bool(getattr(args, "apply_mpy_pin", False)),
    )
    _print_lines(report.lines)
    return 0 if report.ok else 1


def cmd_deploy(args: argparse.Namespace) -> int:
    files = [Path(f) for f in args.files] if args.files else None
    if not args.yes:
        planned = plan_deploy(files, port=args.port, prune=args.prune)
        _print_lines(planned.lines)
        if isinstance(planned, DeployResult):
            return 1
        print("Dry plan only. Re-run with --yes only after operator confirmed identity + write.")
        return 2

    result = deploy(
        files,
        port=args.port,
        yes=True,
        verify=args.verify,
        verify_import=args.verify_import,
        expect_name=args.expect_name,
        expect_version=args.expect_version,
        reset=args.reset,
        prune=args.prune,
    )
    _print_lines(result.lines)
    return 0 if result.ok else 1


def cmd_pull(args: argparse.Namespace) -> int:
    result = pull_device(Path(args.dest), port=args.port)
    _print_lines(result.lines)
    return 0 if result.ok else 1


def cmd_monitor(args: argparse.Namespace) -> int:
    result = monitor_port(port=args.port, duration_s=args.duration, baud=args.baud)
    # stream already printed; append summary lines
    for line in result.lines:
        if line != "---":
            print(line)
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
    w.add_argument("--timeout", type=float, default=180.0, help="seconds (default 180)")
    w.add_argument("--poll", type=float, default=2.0, help="poll interval seconds")
    w.set_defaults(func=cmd_wait_device)

    i = sub.add_parser(
        "inspect",
        help="device inspect (no device writes; optional host mpy-cross pin apply)",
    )
    i.add_argument("--port", default=None, help="explicit COMx / device path")
    i.add_argument(
        "--apply-mpy-pin",
        action="store_true",
        help="write silico.toml + requirements-dev mpy-cross pin from device MicroPython",
    )
    i.set_defaults(func=cmd_inspect)

    dep = sub.add_parser(
        "deploy",
        help="copy files to device; requires --port + --yes; files optional if [deploy].core set",
    )
    dep.add_argument(
        "files",
        nargs="*",
        help="local files (basename = remote). If omitted, use silico.toml [deploy].core",
    )
    dep.add_argument(
        "--port",
        required=True,
        help="explicit COMx after operator confirmed this is the product board",
    )
    dep.add_argument(
        "--yes",
        action="store_true",
        help="operator explicitly confirmed overwrite (required to write)",
    )
    dep.add_argument("--verify", action="store_true", help="import version on device after write")
    dep.add_argument(
        "--verify-import",
        default=None,
        metavar="MOD",
        help="soft check MOD on device (import, or compile-only for boot entry main)",
    )
    dep.add_argument(
        "--prune",
        action="store_true",
        help="after write, remove device .py files not in the deploy set (needs --yes)",
    )
    dep.add_argument("--expect-name", default=None)
    dep.add_argument("--expect-version", default=None)
    dep.add_argument("--reset", action="store_true", help="soft reset after deploy")
    dep.set_defaults(func=cmd_deploy)

    pull = sub.add_parser("pull", help="backup device files to a host directory (read-only)")
    pull.add_argument("dest", help="host directory to write into")
    pull.add_argument("--port", default=None)
    pull.set_defaults(func=cmd_pull)

    mon = sub.add_parser(
        "monitor",
        help="stream USB CDC read-only for a while (does not send Ctrl-C)",
    )
    mon.add_argument("--port", default=None)
    mon.add_argument("--duration", type=float, default=10.0, help="seconds (default 10)")
    mon.add_argument("--baud", type=int, default=115200)
    mon.set_defaults(func=cmd_monitor)

    s = sub.add_parser("scaffold", help="merge GCU plate from versioned template")
    s.add_argument("path", nargs="?", default=".", help="destination directory (default: .)")
    s.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing non-protected plate files (README/spec always protected)",
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

