"""Stage 0 orientation skeleton filled from workspace + doctor facts.

Tools encode manners: agents run ``silico welcome`` (read-only), paste/adapt the
text into chat as Stage **0a**, and only then open the start gate (0b).

See root AGENTS.md Stage 0 and tig/silico#70.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from silico.doctor import run_doctor
from silico.workspace import detect_workspace

# (marker_id, human label, regex that must match somewhere in the orientation)
ORIENTATION_MARKERS: tuple[tuple[str, str, re.Pattern[str]], ...] = (
    (
        "silico",
        "what Silico is",
        re.compile(r"\b[Ss]ilico\b.*\b(spine|host|metal|edge|prompt)\b", re.I | re.S),
    ),
    (
        "gcu",
        "GCU defined / product summary",
        re.compile(r"\bGCU\b.*\b(General Contact Unit|shippable|edge product)\b", re.I | re.S),
    ),
    (
        "role",
        "agent vs operator role",
        re.compile(
            r"\b(I own|agent owns|host path|you own|operator)\b.*\b(judgment|physical|irreversible|confirm)\b"
            r"|\byou own\b.*\b(judgment|physical)\b",
            re.I | re.S,
        ),
    ),
    (
        "readiness",
        "what we know now (readiness)",
        re.compile(
            r"\b(what I know|already checked|workspace mode|machine|Python|Git|board|USB|COM)\b",
            re.I,
        ),
    ),
    (
        "first_ship_map",
        "first-ship map",
        re.compile(
            r"\b(first[- ]?ship map|Day\s*1 map)\b"
            r"|\b(first[- ]?ship|Day\s*1)\b.*\b(map|Stage|Phase|tools|workspace|plate|host gate|metal|USB)\b",
            re.I | re.S,
        ),
    ),
    (
        "next_step",
        "next mutating step after go",
        re.compile(r"\b(Next after go|next step|After go)\b", re.I),
    ),
    (
        "start_gate_after",
        "start gate only after orientation",
        re.compile(
            r"\bstart[- ]?gate\b.*\b(next|after|until)\b"
            r"|\bdo not\b.*\b(start[- ]?first[- ]?ship|start[- ]?day1|start[- ]?gate|bedside ask|chooser)\b.*\buntil\b",
            re.I | re.S,
        ),
    ),
)


@dataclass
class WelcomeReport:
    ok: bool
    lines: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)


def validate_orientation_text(text: str) -> list[str]:
    """Return marker ids missing from an operator-facing orientation message.

    Empty list means the skeleton is present enough for Stage 0a. Used by tests
    and as a lightweight eval so thin tooling-only first turns fail the same
    way a red host gate does (tig/silico#70).
    """
    missing: list[str] = []
    for mid, _label, pat in ORIENTATION_MARKERS:
        if not pat.search(text or ""):
            missing.append(mid)
    return missing


def _first_paragraph(path: Path, *, max_chars: int = 280) -> str:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    lines: list[str] = []
    for line in raw.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            if s.startswith("#") and not lines:
                # keep title without hashes
                title = s.lstrip("#").strip()
                if title and not title.startswith("!["):
                    lines.append(title)
            continue
        if s.startswith("|") or s.startswith("```") or s.startswith("- ["):
            continue
        if s.startswith("![") or s.startswith("<"):
            continue
        # Drop bare image markdown mid-line leftovers
        if "](" in s and s.strip().startswith("!["):
            continue
        lines.append(s)
        if sum(len(x) for x in lines) >= max_chars:
            break
    text = " ".join(lines).strip()
    if len(text) > max_chars:
        text = text[: max_chars - 1].rstrip() + "..."
    return text


def _product_summary(root: Path) -> str:
    """One plain sentence from product docs, or honest thin-docs note."""
    readme = root / "README.md"
    spec = root / "spec.md"
    bits: list[str] = []
    if readme.is_file():
        p = _first_paragraph(readme)
        if p:
            bits.append(p)
    if spec.is_file():
        p = _first_paragraph(spec, max_chars=200)
        if p and (not bits or p.lower() not in bits[0].lower()):
            bits.append(p)
    if not bits:
        return (
            "Product docs look thin or missing (no useful README/spec summary yet). "
            "After go we may need **spec interview mode** rather than inventing domain moat."
        )
    joined = " ".join(bits)
    if len(joined) < 40 and not (spec.is_file() and readme.is_file()):
        return (
            f"From product files: {joined} "
            "(docs still look thin — clarify after go if needed)."
        )
    return joined


def _readiness_bits(doctor_lines: list[str], ws_mode: str) -> str:
    tools: list[str] = []
    for line in doctor_lines:
        if line.startswith("OK: git"):
            tools.append("Git OK")
        elif line.startswith("OK: Python"):
            tools.append(line.replace("OK: ", ""))
        elif line.startswith("Python ") and "(" in line:
            tools.append(line.split("(")[0].strip())
        elif "mpremote available" in line:
            tools.append("mpremote OK")
        elif line.startswith("WARN: git"):
            tools.append("Git missing")
        elif line.startswith("FAIL: need Python"):
            tools.append("Python too old")
    if not tools:
        tools.append("see doctor lines below")
    ports = [l for l in doctor_lines if l.strip().startswith("COM") or "/dev/" in l]
    preferred = any("score=5" in l or "score=6" in l or "score=7" in l or "score=8" in l or "score=9" in l for l in doctor_lines)
    # Prefer explicit doctor wording
    board = "preferred USB board not clearly present yet (ports are hints only — no identity assumed)"
    if any("no serial ports" in l.lower() for l in doctor_lines):
        board = "no serial ports seen yet"
    elif any("no preferred board" in l.lower() for l in doctor_lines):
        board = "no preferred board (score>=50); only demoted adapters or none"
    elif preferred or any("score=" in l and not l.endswith("score=0") for l in doctor_lines):
        # still do not claim identity
        board = "serial port(s) present — treat as hints only until you confirm board identity"
    return (
        f"{', '.join(tools)}; workspace mode={ws_mode}; {board}"
    )


def build_welcome(*, root: Path | None = None) -> list[str]:
    """Return filled Stage 0a orientation lines (read-only; no start gate)."""
    root = (root or Path.cwd()).resolve()
    ws = detect_workspace(root)
    doctor = run_doctor(root=root)
    summary = _product_summary(root)
    readiness = _readiness_bits(doctor.lines, ws.mode)

    if ws.mode == "gcu":
        next_step = (
            "ensure a **local clone** of Silico beside this GCU, editable-install it, "
            "then scaffold/merge the **plate** and green the **host gate** here"
        )
        workspace_line = "we stay in this product checkout"
    elif ws.mode == "silico-package":
        next_step = (
            "open or create the **product GCU** checkout (do not scaffold a customer GCU into silico)"
        )
        workspace_line = "this tree is the silico package — product first ship belongs in a GCU repo"
    else:
        next_step = (
            "lock the **product workspace** (GCU root with spec/README), then local-clone Silico and scaffold"
        )
        workspace_line = "workspace not clearly a GCU root yet"

    # ASCII-only punctuation: Windows consoles often use cp1252; U+2192 (→) crashes print.
    lines = [
        # Agent directive first so tool logs still encode Stage 0 order even if the model
        # only skims the top of the command output.
        "AGENT: Stage **0a** — paste/adapt the operator block below as your first chat message, "
        "then END THE TURN (no host picker / bedside ask in this turn). On the operator's next "
        "short reply, turn 2 FIRST act = structured start gate only (yes/adjust) — never free-text "
        "cliff or \"shall I open the gate?\". Full AGENTS.md text required (not a fetch summarizer).",
        "",
        "Welcome. **Silico** is the open host-first spine for building shippable edge products: "
        "agents build and maintain products on real boards; Silico is the host tooling and plate, "
        "not the product brand. Prompt to metal.",
        "",
        "This session builds a **GCU** (GCU stands for General Contact Unit - Silico's term for one "
        f"shippable edge product: app + board). From the product docs, this GCU is: {summary}",
        "",
        "I'm here to get it shipped. I step through host setup, plate, tests, and the board. "
        "**I own the host path** (setup, tests, deploy tooling); the operator owns product "
        "judgment and confirms physical or irreversible steps.",
        "",
        f"What I know now: {readiness} ({workspace_line}).",
        "",
        "**First-ship map:** (A) machine tools -> (B) product workspace locked -> (C) **plate** via "
        "**scaffold**, then **host gate** (automated tests on this computer) green -> (D) board "
        "talks over USB and a confirmed first deploy with operator-observable **product face**. "
        "We do not stop at host-only.",
        "",
        f"**Next after go:** {next_step} - that gives us a maintainable layout and an honest "
        "host test path before we touch the board.",
        "",
        "---",
        "Orientation done (Stage **0a**).",
        "",
        "**Your next step:** When you have read this, reply with anything short (`ok`, `go`, or "
        "Enter). I will open a **start-gate chooser** (yes / adjust) on the next turn — not a "
        "free-text menu. Do not type a long plan here.",
        "",
        "AGENT turn 2 (after their short reply) — open chooser FIRST, CANONICAL shape only:",
        "  bedside ask --id start-first-ship --prompt \"Start first ship on this machine?\" "
        "--choices yes,adjust --default yes",
        "  Host picker: same id/prompt/choices; say once if using host shell.",
        "  Do not invent Go / Host-only / Look around. Optional: Orientation is in the message above.",
        "",
        "Doctor snapshot (read-only grounding):",
    ]
    for dl in doctor.lines:
        lines.append(f"  {dl}")
    return lines


def run_welcome(*, root: Path | None = None) -> WelcomeReport:
    lines = build_welcome(root=root)
    missing = validate_orientation_text("\n".join(lines))
    if missing:
        lines.append(
            "FAIL: generated welcome missing orientation markers: "
            + ", ".join(missing)
        )
    else:
        lines.append(
            "OK: orientation skeleton complete — show 0a + operator next-step, end turn; "
            "on their short reply open start-gate chooser first (not free-text)."
        )
    return WelcomeReport(ok=not missing, lines=lines, missing=missing)
