"""Host-importability and machine-import allowlist — keep the HAL seam honest.

The Silico deal is: write MicroPython, deploy to metal, prove it on the host with
pytest. That is only honest if domain modules import cleanly under CPython and
only declared device backends touch ``machine``.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path

from silico.config_toml import read_deploy_core, read_hal_allow_machine
from silico.runtime import resolve_runtime


@dataclass
class HygieneReport:
    ok: bool
    lines: list[str] = field(default_factory=list)


def _module_stem(local_path: str) -> str:
    return Path(local_path).stem


def scan_machine_imports(source: str) -> list[tuple[int, str]]:
    """Return (lineno, kind) for each import of the ``machine`` module."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    hits: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "machine" or alias.name.startswith("machine."):
                    hits.append((node.lineno, f"import {alias.name}"))
        elif isinstance(node, ast.ImportFrom):
            if node.module == "machine" or (
                node.module is not None and node.module.startswith("machine.")
            ):
                hits.append((node.lineno, f"from {node.module} import …"))
    return hits


def try_host_import(path: Path, module_name: str, *, firmware_dir: Path) -> str | None:
    """Import ``path`` under CPython. Return error string or None on success.

    Ensures ``firmware_dir`` is on sys.path so sibling firmware imports resolve
    the same way they do on-device.
    """
    if not path.is_file():
        return f"missing file: {path}"
    inserted = False
    fw = str(firmware_dir)
    if fw not in sys.path:
        sys.path.insert(0, fw)
        inserted = True
    # Drop a prior load of this name so re-runs see fresh source.
    sys.modules.pop(module_name, None)
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            return f"cannot load: {path}"
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception as e:  # noqa: BLE001 — gate must surface any import failure
            return f"{type(e).__name__}: {e}"
        return None
    finally:
        if inserted and sys.path and sys.path[0] == fw:
            sys.path.pop(0)


def run_hygiene(root: Path | None = None) -> HygieneReport:
    """Check deploy-core host-importability and machine-import allowlist.

    For ``language = c``, delegates to :func:`silico.gate_c.run_c_gate`.
    """
    root = (root or Path.cwd()).resolve()
    cfg = resolve_runtime(root)
    if cfg.language == "c":
        from silico.gate_c import run_c_gate

        # Include hygiene always. Host gate subprocess only when build/host exists
        # (agent configures first). Tests call run_c_gate(..., run_command=False).
        build_ready = (root / "build" / "host").is_dir()
        report = run_c_gate(root, run_command=build_ready)
        if not build_ready:
            report.lines.append(
                "INFO: skipped [host].gate subprocess (no build/host yet). "
                "Configure: cmake -S host -B build/host"
            )
        return HygieneReport(report.ok, report.lines)

    lines: list[str] = []
    ok = True

    core = read_deploy_core(root)
    if not core:
        lines.append(
            "WARN: no [deploy].core in silico.toml — skip host-import hygiene "
            "(add core file list so the gate can prove the product path)."
        )
        return HygieneReport(True, lines)

    allow = set(read_hal_allow_machine(root))

    # Device-fatal constructs the host can't catch by importing (CPython has
    # __future__; MicroPython does not). A deploy-set file with this import
    # verifies fine and then dies on first boot before the loop starts
    # (tig/silico#46) — exactly the "verifies but doesn't run" class.
    for rel in core:
        p = root / rel
        if not p.is_file() or p.suffix.lower() != ".py":
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if line.strip().startswith("from __future__ import"):
                ok = False
                lines.append(
                    f"FAIL: {rel}:{n} imports __future__ — MicroPython has no "
                    "__future__ module; this deploy-set file will die on device "
                    "before the loop starts (tig/silico#46)."
                )

    firmware_dirs: set[Path] = set()
    for rel in core:
        p = root / rel
        if p.parent.is_dir():
            firmware_dirs.add(p.parent.resolve())
    # Prefer the common plate layout.
    fw_default = (root / "firmware").resolve()
    if fw_default.is_dir():
        firmware_dirs.add(fw_default)
    firmware_dir = next(iter(sorted(firmware_dirs, key=lambda p: str(p))), root)

    lines.append(f"Host hygiene root: {root}")
    lines.append(f"Deploy core: {len(core)} file(s)")
    if allow:
        lines.append("machine allowlist: " + ", ".join(sorted(allow)))
    else:
        lines.append(
            "machine allowlist: (empty — no deploy-core module may import machine; "
            "set [hal].allow_machine for device backends)"
        )

    for rel in core:
        path = (root / rel).resolve()
        stem = _module_stem(rel)
        lines.append(f"— {rel}")

        if not path.is_file():
            lines.append(f"  FAIL: not found")
            ok = False
            continue

        # Binary / non-Python deploy assets are copy-only (audio riffs, etc.).
        if path.suffix.lower() not in {".py"}:
            lines.append(
                "  OK: non-Python deploy asset (copy-only; skip host import / machine scan)"
            )
            continue

        try:
            src = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            lines.append(
                "  OK: non-UTF-8 deploy asset (copy-only; skip host import / machine scan)"
            )
            continue
        machine_hits = scan_machine_imports(src)
        if machine_hits and stem not in allow:
            ok = False
            for lineno, kind in machine_hits:
                lines.append(
                    f"  FAIL: {kind} at line {lineno} — only [hal].allow_machine "
                    f"modules may import machine (stem={stem!r} not allowlisted)"
                )
        elif machine_hits:
            lines.append(
                f"  OK: machine import allowlisted ({len(machine_hits)} site(s))"
            )
        else:
            lines.append("  OK: no machine import")

        err = try_host_import(path, stem, firmware_dir=firmware_dir)
        if err:
            lines.append(f"  FAIL: host import: {err}")
            ok = False
        else:
            lines.append("  OK: host-importable under CPython")

    if ok:
        lines.append("OK: host hygiene passed (importable deploy set; machine allowlist).")
    else:
        lines.append(
            "FAIL: host hygiene — fix before claiming the host gate proves metal-bound code."
        )
    return HygieneReport(ok=ok, lines=lines)
