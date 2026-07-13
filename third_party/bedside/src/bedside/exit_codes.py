"""Stable exit codes for agent-first automation.

Future tui-cs/cli adapters should preserve these values.

0  OK (including recommended ask path / confirmed step)
10 Human needed, declined, or non-recommended ask choice
20 Manners fail (eval expect mismatch)
30 Tool or setup error
"""

OK = 0
HUMAN_NEEDED = 10
MANNERS_FAIL = 20
SETUP_ERROR = 30
