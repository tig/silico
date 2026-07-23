"""Agent-first CLI: thin verbs, clear exit codes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from silico import __version__
from silico.deploy import DeployResult, deploy, plan_deploy
from silico.doctor import run_doctor
from silico.first_flash import FirstFlashResult, first_flash, plan_first_flash
from silico.host_hygiene import run_hygiene
from silico.inspect_device import inspect
from silico.monitor import monitor_port
from silico.board_profile import (
    list_profiles,
    load_profile,
    resolve_profile_id,
    seed_defaults_candidates,
    show_profile_lines,
)
from silico.parts import fetch_parts, load_parts
from silico.welcome import run_welcome
from silico.product_path import run_product_path_check
from silico.pull_device import pull_device
from silico.scaffold import scaffold
from silico.wait_device import TIMEOUT_SOP, format_port_snapshot, wait_for_board


def _out(msg: str) -> None:
    """Operator-facing line (flush so multi-minute flash/deploy is not silent)."""
    print(msg, flush=True)


def _print_lines(lines: list[str]) -> None:
    for line in lines:
        _out(line)


def cmd_doctor(_args: argparse.Namespace) -> int:
    report = run_doctor()
    _print_lines(report.lines)
    return 0 if report.ok else 1


def cmd_welcome(_args: argparse.Namespace) -> int:
    """Phase 0a orientation skeleton from workspace + doctor (before start gate)."""
    report = run_welcome()
    _print_lines(report.lines)
    return 0 if report.ok else 1


def cmd_gate(_args: argparse.Namespace) -> int:
    """Host hygiene: deploy-set importable under CPython; machine allowlist."""
    report = run_hygiene()
    _print_lines(report.lines)
    return 0 if report.ok else 1


def cmd_parts(args: argparse.Namespace) -> int:
    """Part truth: validate parts.toml; --fetch pulls local grounding copies."""
    report = fetch_parts() if args.fetch else load_parts()
    _print_lines(report.lines)
    return 0 if report.ok else 1


def cmd_board_profile(args: argparse.Namespace) -> int:
    """List / show / seed Day-1 product-face pin packs for common boards."""
    action = getattr(args, "bp_action", None) or "list"
    if action == "list":
        profiles = list_profiles()
        if not profiles:
            _out("FAIL: no board profiles packaged.")
            return 1
        _out("Board profiles (Day-1 product-face pin packs):")
        for p in profiles:
            face = p.product_face_summary or "(no face summary)"
            _out(f"  {p.id:16}  {p.name} — {face}")
        linked = resolve_profile_id()
        if linked:
            _out(f"parts.toml links profile: {linked}")
        else:
            _out(
                "No profile linked from parts.toml yet. "
                "Set profile = \"m5go\" (etc.) on the role=board part."
            )
        _out("Show: silico board-profile show <id>")
        _out("Seed defaults candidates (dry-run): silico board-profile seed [id]")
        return 0

    if action == "show":
        pid = args.profile_id or resolve_profile_id()
        if not pid:
            _out(
                "FAIL: pass a profile id or set profile on a board part in parts.toml."
            )
            return 1
        try:
            profile = load_profile(pid)
        except FileNotFoundError as e:
            _out(f"FAIL: {e}")
            return 1
        _print_lines(show_profile_lines(profile))
        return 0

    if action == "seed":
        pid = args.profile_id or resolve_profile_id()
        lines, _changed = seed_defaults_candidates(
            profile_id=pid,
            yes=bool(getattr(args, "yes", False)),
        )
        _print_lines(lines)
        return 0 if not any(l.startswith("FAIL:") for l in lines) else 1

    _out(f"FAIL: unknown board-profile action {action!r}")
    return 1


def cmd_product_path(_args: argparse.Namespace) -> int:
    """Report whether sim exercises shipped defaults (product path)."""
    report = run_product_path_check()
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
        _out(
            "Dry plan only. Re-run with --yes only after operator confirmed identity + write."
        )
        return 2

    # Live PROGRESS lines as each file/stage completes (operators see movement).
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
        on_progress=_out,
    )
    return 0 if result.ok else 1


def cmd_first_flash(args: argparse.Namespace) -> int:
    """First-flash MicroPython (esptool or UF2) with streamed progress."""
    kwargs = dict(
        image=Path(args.image),
        port=args.port,
        chip=args.chip,
        offset=args.offset,
        erase=not args.no_erase,
        uf2_dest=Path(args.uf2_dest) if args.uf2_dest else None,
    )
    if not args.yes:
        planned = plan_first_flash(**kwargs)
        _print_lines(planned.lines)
        if isinstance(planned, FirstFlashResult):
            return 1
        _out(
            "Dry plan only. Re-run with --yes only after operator confirmed board + image."
        )
        return 2

    result = first_flash(**kwargs, yes=True, on_progress=_out)
    return 0 if result.ok else 1


def cmd_pull(args: argparse.Namespace) -> int:
    result = pull_device(Path(args.dest), port=args.port, on_progress=_out)
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
    plate = getattr(args, "plate", None) or "gcu"
    try:
        lines = scaffold(dest, force=args.force, plate=plate)
    except FileExistsError as e:
        print(f"FAIL: {e}")
        return 1
    except FileNotFoundError as e:
        print(f"FAIL: {e}")
        return 1
    _print_lines(lines)
    return 1 if any(l.startswith("WARN:") for l in lines) else 0


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

    wel = sub.add_parser(
        "welcome",
        help="Phase 0a Day 1 orientation skeleton (before start gate); read-only",
    )
    wel.set_defaults(func=cmd_welcome)

    g = sub.add_parser(
        "gate",
        help="host hygiene: mpy import/allowlist, or C include hygiene + [host].gate",
    )
    g.set_defaults(func=cmd_gate)

    pt = sub.add_parser(
        "parts",
        help="part truth: validate parts.toml pointers; --fetch caches local copies",
    )
    pt.add_argument("--fetch", action="store_true", help="download pointers into .silico/parts/ (git-ignored)")
    pt.set_defaults(func=cmd_parts)

    bp = sub.add_parser(
        "board-profile",
        help="Day-1 product-face pin packs: list/show/seed defaults.py candidates",
    )
    bp_sub = bp.add_subparsers(dest="bp_action")
    bp_list = bp_sub.add_parser("list", help="list packaged board profiles")
    bp_list.set_defaults(bp_action="list")
    bp_show = bp_sub.add_parser("show", help="show pin pack / face candidates")
    bp_show.add_argument(
        "profile_id",
        nargs="?",
        default=None,
        help="profile id (default: parts.toml board profile)",
    )
    bp_show.set_defaults(bp_action="show")
    bp_seed = bp_sub.add_parser(
        "seed",
        help="seed firmware/defaults.py from profile candidates (dry-run unless --yes)",
    )
    bp_seed.add_argument(
        "profile_id",
        nargs="?",
        default=None,
        help="profile id (default: parts.toml board profile)",
    )
    bp_seed.add_argument(
        "--yes",
        action="store_true",
        help="write defaults.py after operator confirmed this board map",
    )
    bp_seed.set_defaults(bp_action="seed")
    bp.set_defaults(func=cmd_board_profile, bp_action="list", profile_id=None, yes=False)

    pp = sub.add_parser(
        "product-path",
        help="check sim exercises shipped defaults (not only test-local injects)",
    )
    pp.set_defaults(func=cmd_product_path)

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

    ff = sub.add_parser(
        "first-flash",
        help="first-flash MicroPython (esptool ESP32 or UF2 copy) with live progress",
    )
    ff.add_argument("image", help="firmware .bin (esptool) or .uf2 (mass storage)")
    ff.add_argument(
        "--port",
        default=None,
        help="COMx for esptool path (required unless --uf2-dest)",
    )
    ff.add_argument(
        "--chip",
        default="esp32",
        help="esptool chip id (default esp32; e.g. esp32s3)",
    )
    ff.add_argument(
        "--offset",
        default="0x1000",
        help="write-flash offset (default 0x1000 for classic ESP32)",
    )
    ff.add_argument(
        "--no-erase",
        action="store_true",
        help="skip erase-flash before write (default is erase once)",
    )
    ff.add_argument(
        "--uf2-dest",
        default=None,
        metavar="PATH",
        help="copy UF2 to this path on the boot volume (e.g. E:/fw.uf2)",
    )
    ff.add_argument(
        "--yes",
        action="store_true",
        help="operator confirmed this board + image (required to flash)",
    )
    ff.set_defaults(func=cmd_first_flash)

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
        "--plate",
        default="gcu",
        choices=["gcu", "gcu-c"],
        help="plate template: gcu (MicroPython, default) or gcu-c (ESP-IDF / C)",
    )
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

