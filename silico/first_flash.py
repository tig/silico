"""First-flash MicroPython: esptool (ESP32-class) or UF2 copy (RP2040-class).

App updates after first-flash use ``silico deploy`` (mpremote).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from silico.esptool_util import copy_with_progress, esptool_available, run_esptool_streaming
from silico.ports import IDENTITY_HINT, pick_best_port, port_is_listed
from silico.progress import (
    ProgressCallback,
    ProgressLog,
    file_size,
    format_bytes,
    stage_header,
)


@dataclass
class EsptoolFlashPlan:
    port: str
    image: Path
    chip: str
    offset: str
    erase: bool
    lines: list[str] = field(default_factory=list)


@dataclass
class Uf2FlashPlan:
    image: Path
    dest: Path
    lines: list[str] = field(default_factory=list)


# Union alias for plan_first_flash success path (not a bag of optional fields).
FirstFlashPlan = EsptoolFlashPlan | Uf2FlashPlan


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

    if uf2_dest is not None:
        if image.suffix.lower() != ".uf2":
            return FirstFlashResult(
                False,
                [
                    f"FAIL: --uf2-dest requires a .uf2 image (got {image.name}).",
                    "Do not copy raw .bin firmware to an RP2040 boot volume.",
                    "For ESP32 images use --port with esptool (omit --uf2-dest).",
                ],
            )
        dest = Path(uf2_dest)
        return Uf2FlashPlan(
            image=image,
            dest=dest,
            lines=[
                stage_header("plan", "UF2 first-flash (mass storage copy)"),
                f"  image: {image} ({size_s})",
                f"  dest:  {dest}",
                "This OVERWRITES the MicroPython (or bootloader) image on the board once.",
                "After copy, the volume usually disconnects; wait for a new COM, then silico inspect.",
                "Refusing without --yes after operator confirmed the board and this image.",
            ],
        )

    if image.suffix.lower() == ".uf2":
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

    return EsptoolFlashPlan(
        port=chosen.device,
        image=image,
        chip=chip,
        offset=offset,
        erase=erase,
        lines=[
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
        ],
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
    log = ProgressLog(on_progress)

    if isinstance(planned, FirstFlashResult):
        log.extend(planned.lines)
        return FirstFlashResult(planned.ok, log.lines)

    log.extend(planned.lines)

    if not yes:
        log("ABORTED: pass --yes only after the operator explicitly confirmed first-flash.")
        return FirstFlashResult(False, log.lines)

    if isinstance(planned, Uf2FlashPlan):
        return _run_uf2(planned, log)
    return _run_esptool(planned, log)


def _run_uf2(planned: Uf2FlashPlan, log: ProgressLog) -> FirstFlashResult:
    log(stage_header("uf2-copy", f"{planned.image.name} -> {planned.dest}"))
    try:
        copy_with_progress(planned.image, planned.dest, log=log)
    except OSError as e:
        log(f"FAIL: UF2 copy: {e}")
        return FirstFlashResult(False, log.lines)
    log(
        "OK: UF2 copy finished. Wait for volume disconnect / new COM, then silico inspect."
    )
    return FirstFlashResult(True, log.lines)


def _run_esptool(planned: EsptoolFlashPlan, log: ProgressLog) -> FirstFlashResult:
    if not port_is_listed(planned.port):
        log(
            f"FAIL: port {planned.port} disappeared before flash. Re-discover and re-confirm."
        )
        return FirstFlashResult(False, log.lines)

    if planned.erase:
        log(stage_header("erase", f"{planned.port} chip={planned.chip}"))
        code = run_esptool_streaming(
            ["--chip", planned.chip, "--port", planned.port, "erase-flash"],
            log=log,
        )
        if code != 0:
            log(f"FAIL: esptool erase-flash exit {code}")
            return FirstFlashResult(False, log.lines)
        log("OK: erase-flash")

    log(
        stage_header(
            "write-flash",
            f"{planned.image.name} @ {planned.offset} "
            f"({format_bytes(file_size(planned.image))})",
        )
    )
    code = run_esptool_streaming(
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
        log=log,
    )
    if code != 0:
        log(f"FAIL: esptool write-flash exit {code}")
        return FirstFlashResult(False, log.lines)

    log("OK: write-flash complete")
    log(
        "Next: hard reset if needed, then silico inspect --port "
        f"{planned.port} --apply-mpy-pin (only on modern MicroPython)."
    )
    return FirstFlashResult(True, log.lines)
