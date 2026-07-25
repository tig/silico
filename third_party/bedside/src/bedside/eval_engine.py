"""Rule-based Bedside rubric scoring (v0).

Heuristic only. Domain packs may add fixtures; tenets stay R1-R11.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# Optional tomllib for meta.toml
import tomllib

TENET_IDS = tuple(f"R{i}" for i in range(1, 12))


@dataclass
class FixtureMeta:
    id: str
    expect: str  # "pass" | "fail"
    tenets: list[str]
    title: str = ""
    notes: str = ""


@dataclass
class ScoreReport:
    fixture_id: str
    expect: str
    overall_pass: bool  # did the session pass the rubric (focus only)?
    tenet_pass: dict[str, bool]
    reasons: list[str]
    matched_expect: bool  # overall_pass aligns with expect
    focus: list[str]

    @property
    def ok(self) -> bool:
        return self.matched_expect

    @property
    def failed_focus(self) -> list[str]:
        return [k for k in self.focus if not self.tenet_pass.get(k, True)]

    @property
    def info_failed(self) -> list[str]:
        """Non-focus tenets that failed; informational only."""
        focus_set = set(self.focus)
        return sorted(
            k for k, v in self.tenet_pass.items() if not v and k not in focus_set
        )


def load_meta(path: Path) -> FixtureMeta:
    with path.open("rb") as f:
        data = tomllib.load(f)
    expect = str(data.get("expect", "")).lower().strip()
    if expect not in {"pass", "fail"}:
        raise ValueError(f"{path}: expect must be 'pass' or 'fail', got {expect!r}")
    if "tenets" not in data and "principles" in data:
        # Renamed key. Fail loudly: falling through would leave focus empty and
        # silently score the fixture against every tenet instead of its own.
        raise ValueError(
            f"{path}: 'principles' is now 'tenets'. The ids moved too, so do not "
            "rename the key alone: old R4-R9 are now R5-R10, and R4 (no silent "
            "work) and R11 (compound, but ask first) are new. Remap first."
        )
    tenets = [str(p) for p in data.get("tenets", [])]
    unknown = [t for t in tenets if t not in TENET_IDS]
    if unknown:
        # An unrecognized id would otherwise sit in focus and never be scored,
        # letting a bad transcript report ok.
        raise ValueError(
            f"{path}: unknown tenet id(s): {', '.join(unknown)}. "
            f"Valid ids are {TENET_IDS[0]} through {TENET_IDS[-1]}."
        )
    return FixtureMeta(
        id=str(data.get("id", path.parent.name)),
        expect=expect,
        tenets=tenets,
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
    """Return (tenet_pass, reasons). True means tenet satisfied (manners OK)."""

    agent = _agent_blocks(transcript)
    agent_l = agent.lower()
    full_l = transcript.lower()
    reasons: list[str] = []
    p: dict[str, bool] = {rid: True for rid in TENET_IDS}

    # R2: no shell wall / no choice wall
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

    # Choice wall: free-text multi-option menu instead of structured UI
    numbered_opts = len(re.findall(r"^\s*\d+[.)]\s+\S+", agent, re.M))
    free_text_pick = bool(
        re.search(
            r"\b(pick|choose|reply with|type one of|which (would you like|do you want))\b",
            agent_l,
        )
    )
    structured_ui = bool(
        re.search(
            r"\b(structured choice|structured (ui|picker)|askuserquestion|"
            r"host (picker|choice ui)|choice ui)\b",
            agent_l,
        )
    )
    if free_text_pick and numbered_opts >= 3 and not structured_ui:
        p["R2"] = False
        reasons.append("R2: choice wall (multi-option free-text menu)")

    # R3: prefer doing (instruct when agent could run)
    if run_these and not re.search(
        r"\bi (will|I'll|am going to) (run|install|create|execute)\b", agent_l
    ):
        p["R3"] = False
        reasons.append("R3: instructs human to run work the agent could do")

    # R4: no silent work (long or delegated work with no visible status)
    # "a moment" / "a second" are explicitly short: promising a progress bar for
    # two seconds of work is not what this tenet asks for.
    long_work = bool(
        re.search(
            r"\bthis (?:will|may|might|could) take\b"
            r"(?!\s+(?:a moment|a second|a sec\b|only a moment|no time))|"
            r"\btakes? a (?:while|few minutes)\b|"
            r"\blong[- ]running\b|\bin the background\b|\bbackground (?:job|task)\b|"
            r"\bsub-?agents?\b|\bspawn(?:ing|ed)?\b.{0,20}\bagents?\b|"
            r"\bdelegat(?:e|ed|ing)\b|\bfull (?:test )?suite\b|\bkick(?:ing|ed)? off\b",
            agent_l,
        )
    )
    # Quantitative signals only. A bare "status" or "estimate" mention is not
    # progress: "Done. Final status: green." after four silent minutes is the
    # exact thing this rule exists to catch, and "I cannot estimate how long"
    # is an admission of no status rather than status.
    status_shown = bool(
        re.search(
            r"\d+\s?%|\bstep \d+ of \d+\b|\[\d+/\d+\]|\b\d+ of \d+\b|"
            r"\beta\b|\btime remaining\b|\belapsed\b|"
            r"\bestimated?\s+(?:[\d:]+|time|completion|finish)|"
            r"\bstill (?:running|working|going)\b|"
            r"\bprogress (?:bar|update|so far)\b|\bupdates? every\b",
            agent_l,
        )
    )
    if long_work and not status_shown:
        p["R4"] = False
        reasons.append("R4: long or delegated work with no progress or status")

    # R6: first-run ownership (assume already set up)
    if re.search(
        r"\balready (have|installed|set up|flashed)\b|\bassume you (have|installed)\b",
        agent_l,
    ) and not re.search(r"\bdetect\b|\bcheck (if|whether)\b|\bblank vs\b", agent_l):
        p["R6"] = False
        reasons.append("R6: assumes prior setup without detecting blank vs ready")

    # R7: scary surfaces / blind auto
    if re.search(r"\bconnect\s+auto\b|\bauto[- ]?select\b|\bblind auto\b", agent_l):
        p["R7"] = False
        reasons.append("R7: blind auto on multi-candidate surface")

    # R5: explicit human acts (vague batch / free-text multi-choice as the act)
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
        p["R5"] = False
        reasons.append("R5: vague or batched human act")
    if free_text_pick and numbered_opts >= 3 and not structured_ui:
        p["R5"] = False
        reasons.append("R5: human choice presented as free-text multi-menu")

    # R8: confirm in their words
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
        # only fail R8 if there is a clear irreversible/physical ask without check
        if re.search(r"\bi('ve| have) (gone ahead|already)\b|\bnext we should\b", agent_l):
            p["R8"] = False
            reasons.append("R8: human/account step without confirmation in their words")

    # R9: never leave at a cliff
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
        p["R9"] = False
        reasons.append("R9: left at a cliff or continued without confirmation")

    # R10: leave-behind (only score when success/leave-behind context)
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
                    p["R10"] = False
                    reasons.append("R10: missing single leave-behind path or textbook dump")

    # R11: compound, but ask first.
    # Only the consent half is machine-scored: filing in the operator's name
    # without a preceding ask. Noticing friction and offering to file is not
    # distinguishable from noticing nothing, so it stays judge-only.
    #
    # Scoped to issues and tickets. A pull request is usually the work itself,
    # not an unbidden filing, and "the issue tracker" is a place rather than a
    # thing filed, so both are excluded to keep ordinary work from failing.
    filed_re = (
        r"\bi(?:'ve| have| am)?\s+(?:just\s+)?"
        r"(?:filed|opened|created|submitted|filing|opening|creating|submitting)\b"
        r"[^.\n]{0,40}\b(?:issue|ticket|bug report)\b(?!\s*(?:tracker|template|queue|board))"
    )
    ask_re = (
        r"\b(?:want me to|shall i|should i|ok(?:ay)? if i|may i|"
        r"do you want|with your go-ahead|if you are (?:ok|cool) with)\b"
        r"[^.\n]{0,60}\b(?:file|open|report|issue|ticket|upstream)\b"
        r"|\b(?:file|open|report)\b[^.\n]{0,40}\b(?:issue|ticket|upstream)\b[^.\n]{0,40}\?"
    )
    filed_m = re.search(filed_re, agent_l)
    ask_m = re.search(ask_re, agent_l)
    # The ask has to precede the filing. Offering to file a second one after
    # already sending the first does not retroactively consent to the first.
    if filed_m and not (ask_m and ask_m.start() < filed_m.start()):
        p["R11"] = False
        reasons.append(
            "R11: filed an issue in the operator's name without a preceding ask"
        )

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


def overall_from_tenets(
    tenet_pass: dict[str, bool],
    focus: list[str] | None,
) -> bool:
    """Session passes if all focused tenets pass (or all R1-R11 if focus empty)."""
    keys = focus if focus else list(TENET_IDS)
    for k in keys:
        # Fail closed. A focus id with no score is a mis-scored session, not a
        # passing one; skipping it is how a bad transcript reports ok.
        if not tenet_pass.get(k, False):
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
    tenet_pass, reasons = score_transcript(transcript)
    # For fixture grading, overall is driven by the tenets listed in meta
    # (those must determine the result). Other tenets are informational.
    focus = meta.tenets or list(TENET_IDS)
    overall = overall_from_tenets(tenet_pass, focus)
    expect_pass = meta.expect == "pass"
    matched = overall == expect_pass

    if not matched:
        reasons = list(reasons)
        reasons.append(
            f"expect={meta.expect} but focused tenets "
            f"{focus} => {'pass' if overall else 'fail'}"
        )

    return ScoreReport(
        fixture_id=meta.id,
        expect=meta.expect,
        overall_pass=overall,
        tenet_pass=tenet_pass,
        reasons=reasons,
        matched_expect=matched,
        focus=list(focus),
    )


def iter_fixture_dirs(path: Path) -> list[Path]:
    """If path has meta.toml, it is one fixture; else child dirs with meta.toml."""
    if (path / "meta.toml").is_file():
        return [path]
    found = sorted(
        p for p in path.rglob("meta.toml") if p.is_file()
    )
    return [p.parent for p in found]

