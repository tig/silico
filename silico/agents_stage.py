"""On-demand AGENTS.md stage packs (tig/silico#79).

``silico agents --stage d`` prints only Stage D text from the same canonical
``AGENTS.md`` as the full essay — no second manual. Prefer this over loading
the whole file into every agent turn.
"""

from __future__ import annotations

import re
from pathlib import Path

# heading fragment (lower) -> stage id
_HEADING_TO_ID: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^manners tools are the operator path", re.I), "core"),
    (re.compile(r"^operator gates:", re.I), "gates"),
    (re.compile(r"^stage\s*0\b", re.I), "0"),
    (re.compile(r"^stage\s*a\b", re.I), "a"),
    (re.compile(r"^stage\s*b\b", re.I), "b"),
    (re.compile(r"^stage\s*c\b", re.I), "c"),
    (re.compile(r"^stage\s*d\b", re.I), "d"),
    (re.compile(r"^stage\s*e\b", re.I), "e"),
    (re.compile(r"^stage\s*f\b", re.I), "f"),
    (re.compile(r"^c\s*/\s*esp-idf backend", re.I), "lang-c"),
    (re.compile(r"^definition of done", re.I), "dod"),
    (re.compile(r"^spec interview mode", re.I), "interview"),
]

_ALIAS: dict[str, str] = {
    "core": "core",
    "manners": "core",
    "required": "core",
    "gates": "gates",
    "gate": "gates",
    "ask": "gates",
    "0": "0",
    "stage0": "0",
    "stage-0": "0",
    "welcome": "0",
    "a": "a",
    "stagea": "a",
    "stage-a": "a",
    "tools": "a",
    "b": "b",
    "stageb": "b",
    "stage-b": "b",
    "workspace": "b",
    "c": "c",
    "stagec": "c",
    "stage-c": "c",
    "plate": "c",
    "scaffold": "c",
    "d": "d",
    "staged": "d",
    "stage-d": "d",
    "metal": "d",
    "hello-metal": "d",
    "e": "e",
    "stagee": "e",
    "stage-e": "e",
    "ci": "e",
    "f": "f",
    "stagef": "f",
    "stage-f": "f",
    "domain": "f",
    "lang-c": "lang-c",
    "language-c": "lang-c",
    "idf": "lang-c",
    "esp-idf": "lang-c",
    "gcu-c": "lang-c",
    "dod": "dod",
    "done": "dod",
    "interview": "interview",
    "spec": "interview",
}


def agents_md_path() -> Path | None:
    """Locate canonical AGENTS.md (repo root next to the silico package)."""
    here = Path(__file__).resolve()
    # silico/agents_stage.py -> parents[1] is repo root when editable install
    for parent in here.parents:
        cand = parent / "AGENTS.md"
        if cand.is_file() and (parent / "silico").is_dir():
            return cand
    return None


def _split_h3_sections(text: str) -> list[tuple[str, str]]:
    """Return list of (heading_without_hashes, body) for ### sections."""
    lines = text.splitlines(keepends=True)
    sections: list[tuple[str, str]] = []
    cur_h: str | None = None
    cur_body: list[str] = []
    for line in lines:
        if line.startswith("### "):
            if cur_h is not None:
                sections.append((cur_h, "".join(cur_body).rstrip() + "\n"))
            cur_h = line[4:].strip()
            cur_body = [line]
        elif cur_h is not None:
            # stop at next ## (not ###) top-level? keep going until next ###
            if line.startswith("## ") and not line.startswith("### "):
                sections.append((cur_h, "".join(cur_body).rstrip() + "\n"))
                cur_h = None
                cur_body = []
            else:
                cur_body.append(line)
    if cur_h is not None:
        sections.append((cur_h, "".join(cur_body).rstrip() + "\n"))
    return sections


def index_stages(text: str) -> dict[str, str]:
    """Map stage id -> section markdown body (includes heading line)."""
    out: dict[str, str] = {}
    for heading, body in _split_h3_sections(text):
        for pat, sid in _HEADING_TO_ID:
            if pat.search(heading):
                # first match wins per id (keep first)
                out.setdefault(sid, body)
                break
    return out


def normalize_stage(stage: str) -> str | None:
    key = (stage or "").strip().lower()
    if not key:
        return None
    return _ALIAS.get(key) or _ALIAS.get(key.replace(" ", "-"))


def list_stage_ids(text: str | None = None) -> list[tuple[str, str]]:
    """Return (id, first_heading_line) for available packs."""
    if text is None:
        path = agents_md_path()
        if path is None:
            return []
        text = path.read_text(encoding="utf-8", errors="replace")
    idx = index_stages(text)
    order = ["core", "gates", "0", "a", "b", "c", "d", "e", "f", "lang-c", "interview", "dod"]
    out: list[tuple[str, str]] = []
    for sid in order:
        if sid not in idx:
            continue
        first = idx[sid].splitlines()[0] if idx[sid] else sid
        out.append((sid, first.lstrip("# ").strip()))
    return out


def stage_pack(
    stage: str,
    *,
    agents_path: Path | None = None,
    text: str | None = None,
) -> tuple[bool, list[str]]:
    """Return (ok, lines) for a stage pack or list."""
    key = (stage or "").strip().lower()
    if key in ("list", "help", ""):
        if text is None:
            path = agents_path or agents_md_path()
            if path is None:
                return False, [
                    "FAIL: AGENTS.md not found (install silico from a local clone).",
                ]
            text = path.read_text(encoding="utf-8", errors="replace")
        lines = [
            "Silico stage packs (same source as AGENTS.md). Load only what you need:",
            "  silico agents --stage core   # manners tools hard rules",
            "  silico agents --stage 0      # welcome / start gate",
            "  silico agents --stage d      # hello metal",
            "  silico agents --stage lang-c # C / ESP-IDF backend",
            "",
            "Available:",
        ]
        for sid, title in list_stage_ids(text):
            lines.append(f"  {sid:10}  {title}")
        lines.append("")
        lines.append(
            "Do not paste the full AGENTS.md into every turn when a stage pack suffices (#79)."
        )
        return True, lines

    sid = normalize_stage(stage)
    if sid is None:
        return False, [
            f"FAIL: unknown stage {stage!r}. Try: silico agents --stage list",
        ]

    if text is None:
        path = agents_path or agents_md_path()
        if path is None:
            return False, [
                "FAIL: AGENTS.md not found next to the silico package. "
                "Use an editable install from the silico clone.",
            ]
        text = path.read_text(encoding="utf-8", errors="replace")

    idx = index_stages(text)
    body = idx.get(sid)
    if not body:
        return False, [
            f"FAIL: stage {sid!r} not found in AGENTS.md "
            f"(known: {', '.join(list_stage_ids(text) and [s for s, _ in list_stage_ids(text)])}).",
        ]
    header = [
        f"# silico agents --stage {sid}",
        f"# Source: AGENTS.md (canonical; not a soft-fork)",
        "",
    ]
    return True, header + body.splitlines()
