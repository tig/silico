"""bedside eval: score fixtures against the rubric."""

from __future__ import annotations

import json
from pathlib import Path

from bedside.config import load_config, repo_root_from_package, resolve_under
from bedside.eval_engine import evaluate_fixture_dir, iter_fixture_dirs
from bedside.exit_codes import MANNERS_FAIL, OK, SETUP_ERROR
from bedside.result import CommandResult


def default_fixture_paths(root: Path) -> list[Path]:
    """Resolve default fixture roots from bedside.toml or repo defaults."""
    cfg = load_config(root)
    paths: list[Path] = []
    if cfg and cfg.fixture_paths:
        for rel in cfg.fixture_paths:
            p = resolve_under(root, rel)
            if p.is_dir():
                paths.append(p)
        if paths:
            return paths
    if cfg:
        cand = resolve_under(root, cfg.eval_path) / "fixtures"
        if cand.is_dir():
            paths.append(cand)
    pkg = repo_root_from_package() / "eval" / "fixtures"
    if pkg.is_dir() and pkg not in paths:
        # Prefer project paths; fall back to this checkout when developing bedside.
        if not paths:
            paths.append(pkg)
    return paths


def run_eval(
    root: Path,
    paths: list[Path],
    *,
    json_out: bool = False,
) -> CommandResult:
    root = root.resolve()
    targets: list[Path] = []

    if not paths:
        defaults = default_fixture_paths(root)
        if not defaults:
            r = CommandResult(SETUP_ERROR)
            r.line("No fixture path given and no eval/fixtures found.")
            r.line(
                "What to do next: pass fixture dir(s), set fixture_paths in bedside.toml, "
                "or `bedside init` and vendor tig/bedside."
            )
            return r
        paths = defaults

    seen: set[Path] = set()
    for p in paths:
        p = p if p.is_absolute() else (root / p)
        p = p.resolve()
        if not p.exists():
            r = CommandResult(SETUP_ERROR)
            r.line(f"Path not found: {p}")
            r.line("What to do next: check the path; fixtures need meta.toml + transcript.md.")
            return r
        for fix in iter_fixture_dirs(p):
            if fix not in seen:
                seen.add(fix)
                targets.append(fix)

    if not targets:
        r = CommandResult(SETUP_ERROR)
        r.line("No fixtures found (need meta.toml under the path).")
        r.line("What to do next: point at eval/fixtures or a single fixture directory.")
        return r

    reports = []
    for fix in targets:
        try:
            reports.append(evaluate_fixture_dir(fix))
        except (OSError, ValueError) as e:
            r = CommandResult(SETUP_ERROR)
            r.line(f"Failed to evaluate {fix}: {e}")
            r.line("What to do next: ensure meta.toml and transcript.md are valid.")
            return r

    failed = [rep for rep in reports if not rep.ok]
    code = OK if not failed else MANNERS_FAIL
    r = CommandResult(code)

    if json_out:
        payload = [
            {
                "id": rep.fixture_id,
                "expect": rep.expect,
                "overall_pass": rep.overall_pass,
                "matched_expect": rep.matched_expect,
                "focus": rep.focus,
                "failed_focus": rep.failed_focus,
                "info_failed": rep.info_failed,
                "principles": rep.principle_pass,
                "reasons": rep.reasons,
            }
            for rep in reports
        ]
        r.line(json.dumps({"results": payload, "ok": code == OK}, indent=2))
        return r

    r.line(f"Bedside eval: {len(reports)} fixture(s)")
    for rep in reports:
        mark = "OK" if rep.ok else "FAIL"
        parts = [
            f"[{mark}] {rep.fixture_id}",
            f"expect={rep.expect}",
            f"scored={'pass' if rep.overall_pass else 'fail'}",
        ]
        if rep.failed_focus:
            parts.append(f"failed={','.join(rep.failed_focus)}")
        if rep.info_failed:
            # Non-focus failures: informational only (do not drive expect).
            parts.append(f"info={','.join(rep.info_failed)}")
        r.line("  " + " ".join(parts))
        if not rep.ok:
            for reason in rep.reasons[:5]:
                r.line(f"         {reason}")

    if failed:
        r.line(f"{len(failed)} fixture(s) did not match expect.")
        r.line(
            "What to do next: fix agent path or fixture; re-run until known-bad fails "
            "manners and known-good passes."
        )
    else:
        r.line("All fixtures matched expect.")
        r.line("What to do next: wire `bedside eval` into CI on operator-path changes.")
    return r
