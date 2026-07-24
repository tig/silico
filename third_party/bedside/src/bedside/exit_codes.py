"""Stable exit codes for agent-first automation.

Future tui-cs/cli adapters should preserve these values.

0  OK — valid human selection on ask (recommended or not), or confirmed step.
   For ask: inspect ``choice`` / ``matched_recommended`` (JSON or key=value record).
   Explicit scary yes with default no is still exit 0 (tig/silico#84).
10 Human needed — no answer yet, empty input, step declined, or still pending.
20 Manners fail (eval expect mismatch)
30 Tool or setup error
"""

OK = 0
HUMAN_NEEDED = 10
MANNERS_FAIL = 20
SETUP_ERROR = 30
