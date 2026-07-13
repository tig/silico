"""Command results independent of argparse / future tui-cs/cli."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CommandResult:
    """Pure command outcome; CLI adapters map this to exit codes and stdout."""

    exit_code: int
    messages: list[str] = field(default_factory=list)

    def line(self, text: str) -> None:
        self.messages.append(text)
