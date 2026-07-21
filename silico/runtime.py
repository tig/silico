"""Resolve GCU runtime backend from silico.toml (micropython vs C/ESP-IDF)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from silico.config_toml import (
    read_deploy_mode,
    read_deploy_project,
    read_esp_idf_pin,
    read_host_gate,
    read_runtime_board,
    read_runtime_chip,
    read_runtime_language,
    read_runtime_toolchain,
    read_serial_baud,
)

LANG_MICROPYTHON = "micropython"
LANG_C = "c"
KNOWN_LANGUAGES = frozenset({LANG_MICROPYTHON, LANG_C})
TOOLCHAIN_ESP_IDF = "esp-idf"


@dataclass(frozen=True)
class RuntimeConfig:
    language: str
    toolchain: str | None
    esp_idf: str | None
    chip: str | None
    board: str | None
    deploy_mode: str  # "file-copy" | "idf-flash"
    project: str | None
    host_gate: str | None
    baud: int
    errors: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def is_c(self) -> bool:
        return self.language == LANG_C

    @property
    def is_micropython(self) -> bool:
        return self.language == LANG_MICROPYTHON


def resolve_runtime(root: Path | None = None) -> RuntimeConfig:
    """Load and validate runtime selection.

    Default (no language key): MicroPython file-copy path for existing GCUs.
    ``language = c`` requires toolchain esp-idf (defaulted if omitted).
    """
    root = (root or Path.cwd()).resolve()
    language = read_runtime_language(root)
    toolchain = read_runtime_toolchain(root)
    esp_idf = read_esp_idf_pin(root)
    chip = read_runtime_chip(root)
    board = read_runtime_board(root)
    mode = read_deploy_mode(root)
    project = read_deploy_project(root)
    host_gate = read_host_gate(root)
    baud = read_serial_baud(root)
    errors: list[str] = []

    if language not in KNOWN_LANGUAGES:
        errors.append(
            f"FAIL: unknown [runtime].language={language!r}. "
            f"Supported: {', '.join(sorted(KNOWN_LANGUAGES))}."
        )
        language = LANG_MICROPYTHON  # safe fallback for partial reports

    if language == LANG_C:
        if toolchain is None:
            toolchain = TOOLCHAIN_ESP_IDF
        if toolchain != TOOLCHAIN_ESP_IDF:
            errors.append(
                f"FAIL: [runtime].language=c requires toolchain={TOOLCHAIN_ESP_IDF!r}, "
                f"got {toolchain!r}. Arduino/PlatformIO are not silico dual-runtime paths."
            )
        if mode is None:
            mode = "idf-flash"
        elif mode != "idf-flash":
            errors.append(
                f"FAIL: language=c expects [deploy].mode=idf-flash, got {mode!r}."
            )
        if project is None:
            project = "firmware"
        if host_gate is None:
            host_gate = "cmake --build build/host --target test"
        if chip is None:
            errors.append(
                "WARN: [runtime].chip not set (esptool needs esp32 / esp32s3 / …). "
                "Defaulting plan text to esp32; set chip in silico.toml."
            )
            chip = "esp32"
    else:
        # micropython
        if toolchain and toolchain != "micropython":
            # allow absent; if set to something odd, warn via error list as soft fail
            if toolchain == TOOLCHAIN_ESP_IDF:
                errors.append(
                    "FAIL: toolchain=esp-idf requires language=c (not micropython)."
                )
        if mode is None:
            mode = "file-copy"
        if mode == "idf-flash" and language == LANG_MICROPYTHON:
            errors.append(
                "FAIL: [deploy].mode=idf-flash requires language=c."
            )

    # Hard failures only (WARN lines are still errors tuple for doctor to print soft)
    hard = tuple(e for e in errors if e.startswith("FAIL:"))
    return RuntimeConfig(
        language=language,
        toolchain=toolchain,
        esp_idf=esp_idf,
        chip=chip,
        board=board,
        deploy_mode=mode or "file-copy",
        project=project,
        host_gate=host_gate,
        baud=baud,
        errors=tuple(errors) if hard else tuple(errors),
    )


def runtime_summary_lines(cfg: RuntimeConfig) -> list[str]:
    lines = [
        f"Runtime language: {cfg.language}",
        f"  deploy mode: {cfg.deploy_mode}",
    ]
    if cfg.toolchain:
        lines.append(f"  toolchain: {cfg.toolchain}")
    if cfg.esp_idf:
        lines.append(f"  esp_idf pin: {cfg.esp_idf}")
    if cfg.chip:
        lines.append(f"  chip: {cfg.chip}")
    if cfg.board:
        lines.append(f"  board: {cfg.board}")
    if cfg.project:
        lines.append(f"  project: {cfg.project}")
    if cfg.host_gate:
        lines.append(f"  host gate: {cfg.host_gate}")
    if cfg.baud:
        lines.append(f"  serial baud: {cfg.baud}")
    for e in cfg.errors:
        lines.append(e)
    return lines
