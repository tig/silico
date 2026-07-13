"""Rule-based Bedside rubric scoring (v0).

Heuristic only. Domain packs may add fixtures; principles stay R1-R9.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# Optional tomllib for meta.toml
import tomllib

PRINCIPLE_IDS = tuple(f"R{i}" for i in range(1, 10))


@dataclass
class FixtureMeta:
    id: str
    expect: str  # "pass" | "fail"
    principles: list[str]
    title: str = ""
    notes: str = ""


@dataclass
class ScoreReport:
    fixture_id: str
    expect: str
    overall_pass: bool  # did the session pass the rubric?
    principle_pass: dict[str, bool]
    reasons: list[str]
    matched_expect: bool  # overall_pass aligns with expect

    @property
    def ok(self) -> bool:
        return self.matched_expect


def load_meta(path: Path) -> FixtureMeta:
    with path.open("rb") as f:
        data = tomllib.load(f)
    expect = str(data.get("expect", "")).lower().strip()
    if expect not in {"pass", "fail"}:
        raise ValueError(f"{path}: expect must be 'pass' or 'fail', got {expect!r}")
    principles = [str(p) for p in data.get("principles", [])]
    return FixtureMeta(
        id=str(data.get("id", path.parent.name)),
        expect=expect,
        principles=principles,
        title=str(data.get("title", "")),
        notes=str(data.get("notes", "")),
    )


def _agent_blocks(transcript: str) -> str:
    """Concatenate ## Agent sections (case-insensitive headings)."""
    parts: list[str] = []
    current: list[str] | None = None
    for line in transcript.splitlines():
        if re.match(r"^##\s+agent\s*$", line, re.I):
            if current is not None:
                parts.append("\n".join(current))
            current = []
            continue
        if re.match(r"^##\s+\w+", line) and current is not None:
            parts.append("\n".join(current))
            current = None
            continue
        if current is not None:
            current.append(line)
    if current is not None:
        parts.append("\n".join(current))
    return "\n".join(parts) if parts else transcript


def _count_fenced_blocks(text: str) -> int:
    # triple backtick fences
    return len(re.findall(r"^```", text, re.M)) // 2


def _commandish_lines(text: str) -> int:
    n = 0
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("```"):
            continue
        if re.match(
            r"^(git|python|python3|py|pip|pip3|npm|pnpm|yarn|dotnet|cargo|go|mpremote|"
            r"pytest|curl|wget|ssh|docker|kubectl|brew|choco|winget|cd|mkdir|cp|mv|rm|"
            r"\./|\\\.|source|export|setx?)\b",
            s,
            re.I,
        ):
            n += 1
            continue
        if re.match(r"^[a-z0-9_.-]+\.(ps1|sh|bat|cmd)\b", s, re.I):
            n += 1
    return n


def score_transcript(transcript: str) -> tuple[dict[str, bool], list[str]]:
    """Return (principle_pass, reasons). True means principle satisfied (manners OK)."""

    agent = _agent_blocks(transcript)
    agent_l = agent.lower()
    full_l = transcript.lower()
    reasons: list[str] = []
    p: dict[str, bool] = {rid: True for rid in PRINCIPLE_IDS}

    # R2: no shell wall
    fences = _count_fenced_blocks(agent)
    cmd_lines = _commandish_lines(agent)
    run_these = bool(
        re.search(r"\brun these\b|\brun the following\b|\brun this\b", agent_l)
    )
    if run_these and (fences >= 1 or cmd_lines >= 2):
        p["R2"] = False
        reasons.append("R2: unexplained multi-command dump / 'run these' wall")
    elif cmd_lines >= 4 and run_these:
        p["R2"] = False
        reasons.append("R2: large command wall")

    # R3: prefer doing (instruct when agent could run)
    if run_these and not re.search(
        r"\bi (will|I'll|am going to) (run|install|create|execute)\b", agent_l
    ):
        p["R3"] = False
        reasons.append("R3: instructs human to run work the agent could do")

    # R5: first-run ownership (assume already set up)
    if re.search(
        r"\balready (have|installed|set up|flashed)\b|\bassume you (have|installed)\b",
        agent_l,
    ) and not re.search(r"\bdetect\b|\bcheck (if|whether)\b|\bblank vs\b", agent_l):
        p["R5"] = False
        reasons.append("R5: assumes prior setup without detecting blank vs ready")

    # R6: scary surfaces / blind auto
    if re.search(r"\bconnect\s+auto\b|\bauto[- ]?select\b|\bblind auto\b", agent_l):
        p["R6"] = False
        reasons.append("R6: blind auto on multi-candidate surface")

    # R4: explicit human acts (vague batch)
    batched = bool(
        re.search(
            r"\bdo (all of )?the following\b|\bsteps?:\s*\n.*\n.*\n.*\n",
            agent,
            re.I | re.S,
        )
    )
    vague_physical = bool(
        re.search(r"\byou know the drill\b|\bflash (it|the board)\b(?!.*hold)", agent_l)
    )
    if vague_physical or (batched and re.search(r"\bbrowser\b|\bplug\b|\bhold\b", agent_l)):
        p["R4"] = False
        reasons.append("R4: vague or batched human act")

    # R7: confirm in their words
    needs_human = bool(
        re.search(
            r"\bbrowser\b|\blog\s?in\b|\bpassword\b|\bplug\b|\bhold\b|\bclick\b|"
            r"\bapprove\b|\bdevice code\b|\bauthenticate\b",
            agent_l,
        )
    )
    confirms = bool(
        re.search(
            r"\bdo you (see|have)\b|\btell me when\b|\bconfirm\b|\bi will wait\b|"
            r"\bwait here\b|\bwhen you (see|have)\b",
            agent_l,
        )
    )
    if needs_human and not confirms:
        # only fail R7 if there is a clear irreversible/physical ask without check
        if re.search(r"\bi('ve| have) (gone ahead|already)\b|\bnext we should\b", agent_l):
            p["R7"] = False
            reasons.append("R7: human/account step without confirmation in their words")

    # R8: never leave at a cliff
    cliff = bool(
        re.search(
            r"\bfigure (it|that) out from here\b|\byou can figure\b|"
            r"\bfrom here if anything\b|\bleft (you )?at a cliff\b",
            agent_l,
        )
    )
    continued_early = bool(
        re.search(
            r"\bi('ve| have) (gone ahead|already) (and )?(created|pushed|deployed|finished)\b",
            agent_l,
        )
    ) and needs_human and not confirms
    if cliff or continued_early:
        p["R8"] = False
        reasons.append("R8: left at a cliff or continued without confirmation")

    # R9: Day-2 leave-behind (only score when success/leave-behind context)
    leavebehind_context = bool(
        re.search(
            r"\b(success|finished|done|tomorrow|day 2|update path|leave-behind)\b",
            full_l,
        )
    )
    if leavebehind_context:
        one_path = bool(
            re.search(
                r"\b(only one|one command|update path|tomorrow).{0,80}\n```",
                agent,
                re.I | re.S,
            )
        ) or bool(
            re.search(
                r"\b(only )?one (documented )?(update|command|path)\b",
                agent_l,
            )
        )
        good_looks = bool(
            re.search(r"\bwhat good looks like\b|\bgood looks like\b|\bversion\b.*\bstatus\b", agent_l)
        )
        textbook = bool(
            re.search(
                r"\balternative(ly)?\b.*\balternative\b|\bfive ways\b|\bmultiple ways to\b",
                agent_l,
            )
        )
        if textbook or not (one_path or good_looks):
            # only fail if agent is wrapping up success
            if re.search(r"\b(success|finished successfully|setup finished)\b", agent_l):
                if textbook or not one_path:
                    p["R9"] = False
                    reasons.append("R9: missing single Day-2 path or textbook dump")

    # R1: low ops literacy (only flag egregious "obviously you know git")
    if re.search(
        r"\bobviously you know\b|\bas any developer knows\b|\bjust clone and pip install\b",
        agent_l,
    ):
        p["R1"] = False
        reasons.append("R1: assumes ops literacy")

    if not reasons:
        reasons.append("no rule violations detected")

    return p, reasons


def overall_from_principles(
    principle_pass: dict[str, bool],
    focus: list[str] | None,
) -> bool:
    """Session passes if all focused principles pass (or all R1-R9 if focus empty)."""
    keys = focus if focus else list(PRINCIPLE_IDS)
    for k in keys:
        if k in principle_pass and not principle_pass[k]:
            return False
    return True


def evaluate_fixture_dir(fixture_dir: Path) -> ScoreReport:
    meta_path = fixture_dir / "meta.toml"
    transcript_path = fixture_dir / "transcript.md"
    if not meta_path.is_file():
        raise FileNotFoundError(f"missing meta.toml in {fixture_dir}")
    if not transcript_path.is_file():
        raise FileNotFoundError(f"missing transcript.md in {fixture_dir}")

    meta = load_meta(meta_path)
    transcript = transcript_path.read_text(encoding="utf-8")
    principle_pass, reasons = score_transcript(transcript)
    # For fixture grading, overall is driven by the principles listed in meta
    # (those must determine the result). Other principles are informational.
    focus = meta.principles or list(PRINCIPLE_IDS)
    overall = overall_from_principles(principle_pass, focus)
    expect_pass = meta.expect == "pass"
    matched = overall == expect_pass

    if not matched:
        reasons = list(reasons)
        reasons.append(
            f"expect={meta.expect} but focused principles "
            f"{focus} => {'pass' if overall else 'fail'}"
        )

    return ScoreReport(
        fixture_id=meta.id,
        expect=meta.expect,
        overall_pass=overall,
        principle_pass=principle_pass,
        reasons=reasons,
        matched_expect=matched,
    )


def iter_fixture_dirs(path: Path) -> list[Path]:
    """If path has meta.toml, it is one fixture; else child dirs with meta.toml."""
    if (path / "meta.toml").is_file():
        return [path]
    found = sorted(
        p for p in path.rglob("meta.toml") if p.is_file()
    )
    return [p.parent for p in found]
