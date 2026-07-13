"""bedside step: one human body/browser act, then confirm in their words.

UI-agnostic core. Encodes principles 4, 7, and 8 (one step, confirm, no cliff).
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from typing import TextIO

from bedside.exit_codes import HUMAN_NEEDED, OK, SETUP_ERROR
from bedside.result import CommandResult


def _truthy(raw: str) -> bool | None:
    s = raw.strip().lower()
    if s in {"y", "yes", "true", "1", "confirmed", "done", "ok"}:
        return True
    if s in {"n", "no", "false", "0", "decline", "declined", "cancel", "stop"}:
        return False
    return None


def run_step(
    *,
    gate_id: str,
    prompt: str,
    expect: str | None = None,
    confirm: bool | None = None,
    wait_confirm: bool = True,
    json_out: bool = False,
    input_fn: Callable[[str], str] | None = None,
    stdin_isatty: bool | None = None,
    stdin: TextIO | None = None,
) -> CommandResult:
    """One human step. Exit 0 if confirmed; 10 declined/needed; 30 setup."""
    gate_id = (gate_id or "").strip()
    prompt = (prompt or "").strip()
    if not gate_id:
        r = CommandResult(SETUP_ERROR)
        r.line("step: --id is required (stable step id for logs/eval).")
        r.line("What to do next: `bedside step --id NAME --prompt \"…\"`.")
        return r
    if not prompt:
        r = CommandResult(SETUP_ERROR)
        r.line("step: --prompt is required (one physical or browser instruction).")
        r.line("What to do next: pass a single dumb-simple human act as --prompt.")
        return r

    if not wait_confirm:
        # Show-only path still needs an explicit later confirm; exit human-needed.
        r = CommandResult(HUMAN_NEEDED)
        _emit_step(r, gate_id, prompt, expect)
        r.line("Confirmation not requested on this run (--no-wait).")
        r.line(
            f"Record: bedside.step id={gate_id} confirmed=false wait=false"
        )
        r.line(
            "What to do next: re-run with --confirm after the operator completes the step."
        )
        return r

    confirmed: bool | None = confirm
    if confirmed is None:
        tty = sys.stdin.isatty() if stdin_isatty is None else stdin_isatty
        if not tty and input_fn is None:
            r = CommandResult(HUMAN_NEEDED)
            _emit_step(r, gate_id, prompt, expect)
            r.line(
                "Human action needed: complete the step, then pass --confirm "
                "(or --decline), or answer in a TTY."
            )
            r.line(
                f"Record: bedside.step id={gate_id} confirmed=false pending=true"
            )
            return r
        pre = CommandResult(OK)
        _emit_step(pre, gate_id, prompt, expect)
        # Print before blocking: CLI only flushes CommandResult after return.
        _print_now(pre.messages)
        interactive_flushed = True
        try:
            if input_fn is not None:
                raw = input_fn("Confirm (yes/no): ")
            else:
                stream = stdin if stdin is not None else sys.stdin
                sys.stdout.write("Confirm (yes/no): ")
                sys.stdout.flush()
                raw = stream.readline()
                if not raw:
                    raw = ""
                raw = raw.rstrip("\n\r")
        except EOFError:
            raw = ""
        parsed = _truthy(raw)
        if parsed is None:
            r = CommandResult(SETUP_ERROR)
            # Step already flushed; only error lines for CLI reprint.
            r.line(f"step: could not parse confirmation {raw!r}.")
            r.line("What to do next: answer yes or no (or use --confirm / --decline).")
            return r
        confirmed = parsed
    else:
        interactive_flushed = False

    code = OK if confirmed else HUMAN_NEEDED
    payload = {
        "id": gate_id,
        "prompt": prompt,
        "expect": expect or "",
        "confirmed": confirmed,
    }

    r = CommandResult(code)
    if json_out:
        r.line(json.dumps(payload, ensure_ascii=False))
        return r

    if not interactive_flushed:
        _emit_step(r, gate_id, prompt, expect)
    r.line(f"Confirmed: {'true' if confirmed else 'false'}")
    if not confirmed:
        r.line(
            "Step not confirmed. Do not continue the path (principle 8: no cliff)."
        )
    r.line(
        f"Record: bedside.step id={gate_id} confirmed="
        f"{'true' if confirmed else 'false'}"
    )
    return r


def _print_now(messages: list[str]) -> None:
    """Flush operator-facing lines before a blocking stdin read."""
    for line in messages:
        print(line, flush=True)


def _emit_step(
    r: CommandResult,
    gate_id: str,
    prompt: str,
    expect: str | None,
) -> None:
    r.line(f"Step: {gate_id}")
    r.line(prompt)
    if expect:
        r.line("")
        r.line(f"When done, you should be able to say: {expect}")
    r.line("")
