"""Product-path honesty: host tests must exercise shipped defaults, not only injects.

A green pytest suite that never loads the product's parameter table proves "a
controller can hold a plant," not "the shipped gains hold the plant." Silico
makes shipped defaults a first-class file and reports when sim tests ignore it.
"""

from __future__ import annotations

import ast
import importlib.util
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from silico.config_toml import read_product_defaults_path
from silico.runtime import resolve_runtime


@dataclass
class ProductPathReport:
    ok: bool
    lines: list[str] = field(default_factory=list)
    defaults_path: Path | None = None
    sim_refs: int = 0


def resolve_defaults_path(root: Path | None = None) -> Path | None:
    """Locate the shipped-defaults file (toml override or language-aware convention)."""
    root = (root or Path.cwd()).resolve()
    configured = read_product_defaults_path(root)
    if configured:
        p = (root / configured).resolve()
        return p if p.is_file() else None
    cfg = resolve_runtime(root)
    if cfg.language == "c":
        for alt in (
            root / "include" / "gcu" / "defaults.h",
            root / "src" / "defaults.c",
        ):
            if alt.is_file():
                return alt
        return None
    cand = root / "firmware" / "defaults.py"
    return cand if cand.is_file() else None


def load_shipped_defaults(root: Path | None = None) -> dict[str, object]:
    """Load public names from the defaults module (UPPER_CASE and non-underscore)."""
    root = (root or Path.cwd()).resolve()
    path = resolve_defaults_path(root)
    if path is None:
        return {}
    name = path.stem
    firmware_dir = path.parent
    inserted = False
    fw = str(firmware_dir)
    if fw not in sys.path:
        sys.path.insert(0, fw)
        inserted = True
    sys.modules.pop(name, None)
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            return {}
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        out: dict[str, object] = {}
        for key, val in vars(mod).items():
            if key.startswith("_"):
                continue
            if key != key.upper() and not key[:1].isupper():
                # keep UPPER and CapWords; skip helpers
                if not key.isupper():
                    continue
            out[key] = val
        # Prefer all non-private non-callable module attributes that look like params
        if not out:
            for key, val in vars(mod).items():
                if key.startswith("_") or callable(val):
                    continue
                if isinstance(val, (type(sys), type(re))):
                    continue
                out[key] = val
        return out
    finally:
        if inserted and sys.path and sys.path[0] == fw:
            sys.path.pop(0)


def _sim_files(root: Path) -> list[Path]:
    sim = root / "sim"
    if not sim.is_dir():
        return []
    return sorted(p for p in sim.rglob("*.py") if p.is_file() and p.name != "__init__.py")


def _file_loads_defaults(text: str, stem: str) -> bool:
    """True only if this source *actually reaches* the defaults module.

    Detected via AST, never raw text. A test named ``test_product_path``, a
    docstring mentioning shipped defaults, or a ``# product_path`` comment must
    NOT satisfy this check: a gate that a comment can pass is exactly the
    green-but-broken gate this module exists to prevent.

    Counts as a real reference:
      * ``import defaults`` / ``from defaults import X``
      * attribute access on the module name (``defaults.TICK_SLEEP_MS``)
      * the module name or its filename as a *call argument*, which covers the
        dynamic-load idiom (``_load("defaults")``, ``import_module("defaults")``)
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] == stem for a in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] == stem:
                return True
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == stem:
                return True
        elif isinstance(node, ast.Call):
            # _load("defaults"), import_module("defaults"), spec_from_file_location(...)
            for arg in list(node.args) + [kw.value for kw in node.keywords]:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    val = arg.value
                    if val == stem or Path(val).stem == stem:
                        return True
    return False


def count_defaults_references(root: Path, defaults_stem: str) -> tuple[int, list[str]]:
    """Count sim files that genuinely load the shipped-defaults module."""
    hits = 0
    details: list[str] = []
    for path in _sim_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if _file_loads_defaults(text, defaults_stem):
            hits += 1
            details.append(str(path.relative_to(root)))
    return hits, details


def scan_literal_controller_overrides(sim_path: Path) -> list[str]:
    """Heuristic: flag tests that assign common gain names to numeric literals.

    Not always wrong — surfaces in the report so agents notice pure injects.
    """
    smells: list[str] = []
    try:
        src = sim_path.read_text(encoding="utf-8")
        tree = ast.parse(src)
    except (OSError, SyntaxError):
        return smells
    gain_names = {"kp", "ki", "kd", "gain", "setpoint", "target_rpm", "duty_min", "duty_max"}

    def _is_number(node: ast.AST) -> bool:
        # ast.Num was removed in Python 3.12; Constant covers every literal.
        return isinstance(node, ast.Constant) and isinstance(node.value, (int, float))

    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg and node.arg.lower() in gain_names:
            if _is_number(node.value):
                smells.append(f"{sim_path.name}:{getattr(node, 'lineno', '?')} {node.arg}=literal")
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.lower() in gain_names:
                    if _is_number(node.value):
                        smells.append(
                            f"{sim_path.name}:{getattr(node, 'lineno', '?')} {t.id}=literal"
                        )
    return smells


def _host_c_files(root: Path) -> list[Path]:
    host = root / "host"
    if not host.is_dir():
        return []
    out: list[Path] = []
    for pat in ("**/*.c", "**/*.h", "**/*.cpp"):
        out.extend(p for p in host.glob(pat) if p.is_file())
    return sorted(set(out))


def _strip_c_comments_and_strings(text: str) -> str:
    """Remove // and /* */ comments so greps cannot pass on comment-only mentions."""
    # Block comments first
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    # Line comments
    text = re.sub(r"//.*?$", " ", text, flags=re.MULTILINE)
    return text


def _c_file_uses_defaults(text: str, defaults_path: Path) -> bool:
    """True if source *code* includes defaults and uses a shipped symbol.

    Comments do not count. Bare ``#include`` without using a symbol does not count.
    """
    code = _strip_c_comments_and_strings(text)
    stem = defaults_path.stem
    name = defaults_path.name
    include_hit = (
        f'#include "{name}"' in code
        or f"#include <{name}>" in code
        or f'#include "gcu/{name}"' in code
        or f"#include <gcu/{name}>" in code
        or f'#include "{stem}.h"' in code
        or f'#include "gcu/{stem}.h"' in code
    )
    if not include_hit:
        return False
    # Must use a shipped table/symbol in code (not only include for side effects).
    symbols = (
        "GCU_DEFAULTS",
        "GCU_TICK_SLEEP_MS",
        "gcu_defaults",
        "defaults_table",
    )
    if stem.isidentifier() and stem.upper() not in symbols:
        symbols = (*symbols, stem.upper())
    return any(s in code for s in symbols)


def count_c_defaults_references(root: Path, defaults_path: Path) -> tuple[int, list[str]]:
    hits = 0
    details: list[str] = []
    for path in _host_c_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if _c_file_uses_defaults(text, defaults_path):
            hits += 1
            details.append(str(path.relative_to(root)))
    return hits, details


def run_product_path_check(root: Path | None = None) -> ProductPathReport:
    """Report whether host tests exercise shipped defaults when a defaults module exists."""
    root = (root or Path.cwd()).resolve()
    lines: list[str] = []
    cfg = resolve_runtime(root)
    declared = read_product_defaults_path(root)
    path = resolve_defaults_path(root)

    if path is None and declared:
        # Declaring a shipped-defaults table and not shipping it is a broken
        # product, not an unconfigured one. Skipping here would let CI stay green
        # on a typo in silico.toml.
        lines.append(
            f"FAIL: silico.toml [host].product_defaults = {declared!r} but that file "
            f"does not exist under {root}."
        )
        lines.append(
            "  The product declares a shipped parameter table that cannot be loaded. "
            "Fix the path or remove the setting — do not leave it dangling."
        )
        return ProductPathReport(ok=False, lines=lines, defaults_path=None, sim_refs=0)

    if path is None:
        lines.append(
            "INFO: no shipped defaults file (and no [host].product_defaults) — "
            "product-path check skipped. Add firmware/defaults.py (mpy) or "
            "include/.../defaults.h (C) and at least one host test that uses it."
        )
        return ProductPathReport(ok=True, lines=lines, defaults_path=None, sim_refs=0)

    lines.append(f"Shipped defaults: {path.relative_to(root)}")

    # --- C / language=c only (do not branch on file suffix alone) ---
    if cfg.language == "c":
        refs, detail = count_c_defaults_references(root, path)
        lines.append(f"Host C files using shipped defaults (compiled use): {refs}")
        for d in detail:
            lines.append(f"  ref: {d}")
        ok = True
        if refs == 0:
            ok = False
            lines.append(
                "FAIL: defaults file exists but no host C test uses it. "
                "At least one host test must #include the defaults header and "
                "reference a shipped symbol in code (e.g. GCU_DEFAULTS). "
                "Comments and bare includes do not count."
            )
        else:
            lines.append(f"OK: {refs} host C file(s) exercise shipped defaults.")
        return ProductPathReport(ok=ok, lines=lines, defaults_path=path, sim_refs=refs)

    # --- MicroPython / pytest path ---
    defaults = load_shipped_defaults(root)
    if defaults:
        preview = ", ".join(f"{k}={v!r}" for k, v in list(defaults.items())[:8])
        lines.append(f"  params ({len(defaults)}): {preview}")
    else:
        lines.append("  WARN: defaults module loaded but exported no parameters")

    stem = path.stem
    refs, detail = count_defaults_references(root, stem)
    lines.append(f"Sim files referencing shipped defaults / product_path: {refs}")
    for d in detail:
        lines.append(f"  ref: {d}")

    smells: list[str] = []
    for sim_f in _sim_files(root):
        smells.extend(scan_literal_controller_overrides(sim_f))
    if smells:
        lines.append(
            f"INFO: {len(smells)} possible constant-inject site(s) in sim "
            "(not always wrong — confirm shipped defaults are also covered):"
        )
        for s in smells[:12]:
            lines.append(f"  smell: {s}")

    ok = True
    if refs == 0:
        ok = False
        lines.append(
            "FAIL: defaults module exists but no sim test actually loads it. "
            "At least one host scenario must drive the product with *shipped* "
            "values (unmodified), not only test-local gains/plants. "
            f"Import {stem} in sim/, or load it dynamically — a test *named* for the "
            "product path, or a comment mentioning it, does not count."
        )
    else:
        lines.append(f"OK: {refs} sim file(s) load the shipped defaults module.")

    lines.append(
        "Rule: if the GCU has a control loop, include a closed-loop scenario using "
        "shipped defaults against the plant; fail if the loop cannot reach setpoint."
    )
    return ProductPathReport(ok=ok, lines=lines, defaults_path=path, sim_refs=refs)
