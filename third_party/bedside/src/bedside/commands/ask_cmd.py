"""bedside ask: one structured operator choice (yes/no or multi-choice).

UI-agnostic core. Argparse or a future tui-cs/cli host renders the same result.
Prefers integration with agent structured question UIs; CLI stdin is the fallback.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from typing import TextIO

from bedside.exit_codes import HUMAN_NEEDED, OK, SETUP_ERROR
from bedside.result import CommandResult


def parse_choices(raw: str) -> list[str]:
    """Split comma-separated choices; preserve order; drop empties."""
    parts = [p.strip() for p in raw.split(",")]
    return [p for p in parts if p]


def order_choices(choices: list[str], recommended: str) -> list[str]:
    """Recommended first, then remaining choices in original order."""
    rest = [c for c in choices if c != recommended]
    return [recommended] + rest


def resolve_choice(answer: str, choices: list[str]) -> str | None:
    """Match by exact label or 1-based index. Case-insensitive label fallback."""
    answer = answer.strip()
    if not answer:
        return None
    if answer in choices:
        return answer
    if answer.isdigit():
        idx = int(answer)
        if 1 <= idx <= len(choices):
            return choices[idx - 1]
    lower_map = {c.lower(): c for c in choices}
    return lower_map.get(answer.lower())


def run_ask(
    *,
    gate_id: str,
    prompt: str,
    choices: list[str] | None = None,
    default: str | None = None,
    answer: str | None = None,
    json_out: bool = False,
    input_fn: Callable[[str], str] | None = None,
    stdin_isatty: bool | None = None,
    stdin: TextIO | None = None,
) -> CommandResult:
    """One structured gate. Exit 0 if recommended chosen; 10 declined/needed; 30 setup."""
    gate_id = (gate_id or "").strip()
    prompt = (prompt or "").strip()
    if not gate_id:
        r = CommandResult(SETUP_ERROR)
        r.line("ask: --id is required (stable gate id for logs/eval).")
        r.line("What to do next: `bedside ask --id NAME --prompt \"…\"`.")
        return r
    if not prompt:
        r = CommandResult(SETUP_ERROR)
        r.line("ask: --prompt is required (plain-language question).")
        r.line("What to do next: pass --prompt with one short operator question.")
        return r

    if choices is None:
        choices = ["yes", "no"]
    if len(choices) < 2:
        r = CommandResult(SETUP_ERROR)
        r.line("ask: need at least two --choices.")
        r.line("What to do next: e.g. `--choices yes,no` or `--choices a,b,c`.")
        return r
    # Case-insensitive uniqueness (resolve_choice matches case-insensitively).
    if len({c.lower() for c in choices}) != len(choices):
        r = CommandResult(SETUP_ERROR)
        r.line("ask: choices must be unique (case-insensitive).")
        r.line("What to do next: remove duplicate labels from --choices (e.g. Yes/yes).")
        return r

    recommended = default if default is not None else choices[0]
    if recommended not in choices:
        r = CommandResult(SETUP_ERROR)
        r.line(f"ask: --default {recommended!r} is not in choices {choices}.")
        r.line("What to do next: set --default to one of the choice labels.")
        return r

    ordered = order_choices(choices, recommended)

    selected: str | None = None
    interactive_flushed = False
    if answer is not None:
        selected = resolve_choice(answer, ordered)
        if selected is None:
            r = CommandResult(SETUP_ERROR)
            r.line(f"ask: answer {answer!r} is not a valid choice.")
            r.line(f"What to do next: pick one of {ordered} (or 1-{len(ordered)}).")
            return r
    else:
        tty = sys.stdin.isatty() if stdin_isatty is None else stdin_isatty
        if not tty and input_fn is None:
            r = CommandResult(HUMAN_NEEDED)
            _emit_prompt(r, gate_id, prompt, ordered, recommended)
            r.line(
                "Human action needed: pass --answer LABEL, or run in a TTY, "
                "or use the agent host structured choice UI for this gate."
            )
            r.line(
                f"Record: bedside.ask id={gate_id} choice= pending "
                f"recommended={recommended} matched=false"
            )
            return r
        pre = CommandResult(OK)
        _emit_prompt(pre, gate_id, prompt, ordered, recommended)
        # Print before blocking: CLI only flushes CommandResult after return.
        _print_now(pre.messages)
        interactive_flushed = True
        try:
            if input_fn is not None:
                raw = input_fn("Answer: ")
            else:
                stream = stdin if stdin is not None else sys.stdin
                sys.stdout.write("Answer: ")
                sys.stdout.flush()
                raw = stream.readline()
                if not raw:
                    raw = ""
                raw = raw.rstrip("\n\r")
        except EOFError:
            raw = ""
        selected = resolve_choice(raw, ordered)
        if selected is None:
            r = CommandResult(SETUP_ERROR)
            # Prompt already flushed; only error lines for CLI reprint.
            r.line(f"ask: answer {raw!r} is not a valid choice.")
            r.line(f"What to do next: pick one of {ordered} (or 1-{len(ordered)}).")
            return r

    matched = selected == recommended
    code = OK if matched else HUMAN_NEEDED

    payload = {
        "id": gate_id,
        "prompt": prompt,
        "choices": ordered,
        "recommended": recommended,
        "choice": selected,
        "matched_recommended": matched,
    }

    r = CommandResult(code)
    if json_out:
        r.line(json.dumps(payload, ensure_ascii=False))
        return r

    if not interactive_flushed:
        _emit_prompt(r, gate_id, prompt, ordered, recommended)
    r.line(f"Selected: {selected}")
    r.line(f"matched_recommended: {'true' if matched else 'false'}")
    if not matched:
        r.line(
            "Not the recommended path. Agent should treat this as human declined "
            "or alternate fork (exit 10)."
        )
    r.line(
        f"Record: bedside.ask id={gate_id} choice={selected} "
        f"recommended={recommended} matched={'true' if matched else 'false'}"
    )
    return r


def _print_now(messages: list[str]) -> None:
    """Flush operator-facing lines before a blocking stdin read."""
    for line in messages:
        print(line, flush=True)


def _emit_prompt(
    r: CommandResult,
    gate_id: str,
    prompt: str,
    ordered: list[str],
    recommended: str,
) -> None:
    r.line(f"Gate: {gate_id}")
    r.line(prompt)
    r.line("")
    r.line("Choices (recommended first):")
    for i, c in enumerate(ordered, start=1):
        mark = "  [recommended]" if c == recommended else ""
        r.line(f"  {i}. {c}{mark}")
    r.line("")
