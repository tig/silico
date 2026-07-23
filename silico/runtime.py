"""Resolve GCU runtime backend from silico.toml (micropython vs C/ESP-IDF)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from silico.config_toml import _load

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
    deploy_mode: str  # "file-copy" | "idf-flash" | "none"
    project: str | None
    host_gate: str | None
    baud: int
    errors: tuple[str, ...] = ()  # FAIL lines only
    warnings: tuple[str, ...] = ()  # WARN lines only

    @property
    def ok(self) -> bool:
        """True when safe to select a deploy backend (no FAIL errors)."""
        return not self.errors

    @property
    def is_c(self) -> bool:
        return self.language == LANG_C and self.ok

    @property
    def is_micropython(self) -> bool:
        return self.language == LANG_MICROPYTHON and self.ok


def _str_field(section: dict, key: str) -> str | None:
    raw = section.get(key)
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return None


def resolve_runtime(root: Path | None = None) -> RuntimeConfig:
    """Load and validate runtime selection from one silico.toml parse.

    Default (no language key): MicroPython file-copy for existing GCUs.
    Unknown language fails closed (errors set; not treated as micropython).
    """
    root = (root or Path.cwd()).resolve()
    data = _load(root)
    runtime = data.get("runtime") if isinstance(data.get("runtime"), dict) else {}
    deploy = data.get("deploy") if isinstance(data.get("deploy"), dict) else {}
    host = data.get("host") if isinstance(data.get("host"), dict) else {}

    lang_raw = _str_field(runtime, "language")
    language = (lang_raw or LANG_MICROPYTHON).lower()
    toolchain = _str_field(runtime, "toolchain")
    if toolchain:
        toolchain = toolchain.lower()
    esp_idf = _str_field(runtime, "esp_idf")
    chip = _str_field(runtime, "chip")
    if chip:
        chip = chip.lower()
    board = _str_field(runtime, "board")
    mode = _str_field(deploy, "mode")
    if mode:
        mode = mode.lower()
    project = _str_field(deploy, "project")
    host_gate = _str_field(host, "gate")
    baud_raw = runtime.get("baud")
    if isinstance(baud_raw, int) and baud_raw > 0:
        baud = baud_raw
    elif isinstance(baud_raw, str) and baud_raw.strip().isdigit():
        baud = int(baud_raw.strip())
    else:
        baud = 115200

    errors: list[str] = []
    warnings: list[str] = []

    if language not in KNOWN_LANGUAGES:
        errors.append(
            f"FAIL: unknown [runtime].language={language!r}. "
            f"Supported: {', '.join(sorted(KNOWN_LANGUAGES))}."
        )
        return RuntimeConfig(
            language=language,
            toolchain=toolchain,
            esp_idf=esp_idf,
            chip=chip,
            board=board,
            deploy_mode=mode or "none",
            project=project,
            host_gate=host_gate,
            baud=baud,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

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
            host_gate = "cmake --build build/host --target host_test"
        if chip is None:
            warnings.append(
                "WARN: [runtime].chip not set (esptool needs esp32 / esp32s3 / …). "
                "Defaulting plan text to esp32; set chip in silico.toml."
            )
            chip = "esp32"
    else:
        if toolchain == TOOLCHAIN_ESP_IDF:
            errors.append(
                "FAIL: toolchain=esp-idf requires language=c (not micropython)."
            )
        if mode is None:
            mode = "file-copy"
        if mode == "idf-flash":
            errors.append("FAIL: [deploy].mode=idf-flash requires language=c.")

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
        errors=tuple(errors),
        warnings=tuple(warnings),
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
    for w in cfg.warnings:
        lines.append(w)
    return lines
