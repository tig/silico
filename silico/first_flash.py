"""First-flash MicroPython: esptool (ESP32-class) or UF2 copy (RP2040-class).

App updates after first-flash use ``silico deploy`` (mpremote). This module is
the once-per-board runtime image path, with operator-visible progress.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from silico.esptool_util import (
    copy_with_progress,
    esptool_available,
    run_esptool_streaming,
)
from silico.ports import IDENTITY_HINT, pick_best_port, port_is_listed
from silico.progress import ProgressCallback, emit, file_size, format_bytes, stage_header


@dataclass
class FirstFlashPlan:
    mode: str  # "esptool" | "uf2"
    port: str | None
    image: Path
    chip: str
    offset: str
    erase: bool
    uf2_dest: Path | None
    lines: list[str] = field(default_factory=list)


@dataclass
class FirstFlashResult:
    ok: bool
    lines: list[str] = field(default_factory=list)


def plan_first_flash(
    *,
    image: Path,
    port: str | None = None,
    chip: str = "esp32",
    offset: str = "0x1000",
    erase: bool = True,
    uf2_dest: Path | str | None = None,
) -> FirstFlashPlan | FirstFlashResult:
    image = Path(image)
    if not image.is_file():
        return FirstFlashResult(False, [f"FAIL: image not found: {image}"])

    size = file_size(image)
    size_s = format_bytes(size) if size >= 0 else "?"

    # UF2 path: explicit dest volume/file, or .uf2 suffix without --port write via esptool
    if uf2_dest is not None:
        dest = Path(uf2_dest)
        lines = [
            stage_header("plan", "UF2 first-flash (mass storage copy)"),
            f"  image: {image} ({size_s})",
            f"  dest:  {dest}",
            "This OVERWRITES the MicroPython (or bootloader) image on the board once.",
            "After copy, the volume usually disconnects; wait for a new COM, then silico inspect.",
            "Refusing without --yes after operator confirmed the board and this image.",
        ]
        return FirstFlashPlan(
            mode="uf2",
            port=None,
            image=image,
            chip=chip,
            offset=offset,
            erase=erase,
            uf2_dest=dest,
            lines=lines,
        )

    if image.suffix.lower() == ".uf2" and uf2_dest is None:
        return FirstFlashResult(
            False,
            [
                "FAIL: UF2 image requires --uf2-dest (path to RPI-RP2 volume file, e.g. E:/firmware.uf2).",
                "For ESP32 binary images use --port and omit --uf2-dest.",
            ],
        )

    if not esptool_available():
        return FirstFlashResult(
            False,
            [
                "FAIL: esptool not available (pip install esptool).",
                "Needed for ESP32-class first-flash with progress streaming.",
            ],
        )

    if not port:
        return FirstFlashResult(
            False,
            [
                "FAIL: esptool first-flash requires --port after operator confirms board identity.",
            ],
        )

    chosen = pick_best_port(port)
    if chosen is None:
        return FirstFlashResult(False, ["FAIL: no preferred board port. Use wait-device or --port."])
    if not port_is_listed(chosen.device):
        return FirstFlashResult(
            False,
            [f"FAIL: port {chosen.device} not in serial inventory. Re-run wait-device."],
        )

    lines = [
        stage_header("plan", f"esptool first-flash on {chosen.device}"),
        f"  port:   {chosen.device} ({chosen.label})",
        f"  chip:   {chip}",
        f"  image:  {image} ({size_s})",
        f"  offset: {offset}",
        f"  erase:  {'yes (erase-flash first)' if erase else 'no'}",
        IDENTITY_HINT,
        "This ERASES/overwrites the chip runtime once. App deploys later use silico deploy.",
        "Operator must confirm: (1) this is the product board, (2) this image is correct.",
        "Refusing without --yes.",
        "Progress: esptool percentages stream as PROGRESS [esptool] lines.",
    ]
    return FirstFlashPlan(
        mode="esptool",
        port=chosen.device,
        image=image,
        chip=chip,
        offset=offset,
        erase=erase,
        uf2_dest=None,
        lines=lines,
    )


def first_flash(
    *,
    image: Path,
    port: str | None = None,
    chip: str = "esp32",
    offset: str = "0x1000",
    erase: bool = True,
    uf2_dest: Path | str | None = None,
    yes: bool = False,
    on_progress: ProgressCallback | None = None,
) -> FirstFlashResult:
    planned = plan_first_flash(
        image=image,
        port=port,
        chip=chip,
        offset=offset,
        erase=erase,
        uf2_dest=uf2_dest,
    )
    if isinstance(planned, FirstFlashResult):
        if on_progress:
            for line in planned.lines:
                on_progress(line)
        return planned

    lines: list[str] = []
    for line in planned.lines:
        emit(lines, line, on_progress=on_progress)

    if not yes:
        emit(
            lines,
            "ABORTED: pass --yes only after the operator explicitly confirmed first-flash.",
            on_progress=on_progress,
        )
        return FirstFlashResult(False, lines)

    if planned.mode == "uf2":
        assert planned.uf2_dest is not None
        emit(
            lines,
            stage_header("uf2-copy", f"{planned.image.name} -> {planned.uf2_dest}"),
            on_progress=on_progress,
        )
        try:
            copy_with_progress(planned.image, planned.uf2_dest, on_progress=on_progress)
        except OSError as e:
            emit(lines, f"FAIL: UF2 copy: {e}", on_progress=on_progress)
            return FirstFlashResult(False, lines)
        emit(lines, "OK: UF2 copy finished. Wait for volume disconnect / new COM, then silico inspect.", on_progress=on_progress)
        return FirstFlashResult(True, lines)

    # esptool path
    assert planned.port is not None
    if not port_is_listed(planned.port):
        emit(
            lines,
            f"FAIL: port {planned.port} disappeared before flash. Re-discover and re-confirm.",
            on_progress=on_progress,
        )
        return FirstFlashResult(False, lines)

    if planned.erase:
        emit(lines, stage_header("erase", f"{planned.port} chip={planned.chip}"), on_progress=on_progress)
        r = run_esptool_streaming(
            ["--chip", planned.chip, "--port", planned.port, "erase-flash"],
            on_progress=on_progress,
        )
        if r.returncode != 0:
            emit(lines, f"FAIL: esptool erase-flash exit {r.returncode}", on_progress=on_progress)
            return FirstFlashResult(False, lines)
        emit(lines, "OK: erase-flash", on_progress=on_progress)

    emit(
        lines,
        stage_header(
            "write-flash",
            f"{planned.image.name} @ {planned.offset} ({format_bytes(file_size(planned.image))})",
        ),
        on_progress=on_progress,
    )
    r = run_esptool_streaming(
        [
            "--chip",
            planned.chip,
            "--port",
            planned.port,
            "write-flash",
            "-z",
            planned.offset,
            str(planned.image),
        ],
        on_progress=on_progress,
    )
    if r.returncode != 0:
        emit(lines, f"FAIL: esptool write-flash exit {r.returncode}", on_progress=on_progress)
        return FirstFlashResult(False, lines)

    emit(lines, "OK: write-flash complete", on_progress=on_progress)
    emit(
        lines,
        "Next: hard reset if needed, then silico inspect --port "
        f"{planned.port} --apply-mpy-pin (only on modern MicroPython).",
        on_progress=on_progress,
    )
    return FirstFlashResult(True, lines)
