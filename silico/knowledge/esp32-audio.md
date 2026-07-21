# ESP32 audio on the host path (self-improving)

Generic board/runtime notes for GCUs that **play tones, riffs, or instrument-like audio** on classic ESP32 (internal DAC and/or PWM). Not product song lists or vertical moats.

When you learn a new host truth on a bench, **add a bullet here** (or a sibling file + INDEX row).

## Hardware map (classic ESP32)

| Resource | Typical pins | Use |
|----------|--------------|-----|
| DAC1 | GPIO **25** | 8-bit analog out; often wired to on-board speaker amp |
| DAC2 | GPIO **26** | Second DAC; also common for Grove “signal” / PWM |
| LEDC PWM | most GPIOs | Square / edge trains; fine for tach; harsh for “music” |
| I2S → internal DAC | 25/26 via I2S peripheral | Better sample streams (see prior art below) |

Board schematics differ (amp enable, AC couple). Always ground in the product’s `parts.toml` / board docs before claiming metal audio.

## Tones vs samples

| Need | Prefer | Avoid |
|------|--------|--------|
| Tach / edge honesty to a DUT | Hardware **PWM** with true `duty_pct` | Encoding “volume” by thinning duty (sounds like hash) |
| Short UI chirps | PWM or DAC square with clean park | Leaving LEDC at duty 0 |
| Boot riff / PCM (u8 mono) | DAC sample loop or **I2S+DAC** | `time.sleep_us` alone for pacing (jitter → distortion) |
| Polyphonic / soft synth | I2S + FreeRTOS-style continuous buffer | Bit-banging DAC from the UI tick |

## Silence is hard (bench-proven)

- **PWM duty 0 is not silence** on many ESP32 + amp boards — the LEDC channel still drives the amp. **Deinit PWM** and rebind the pin as **GPIO OUT low** (or board-documented idle).
- Dropping a Python `DAC` reference may **not** unmux the pin. Write a quiet level, then rebind GPIO.
- After sample playback: fade to **u8 mid (128)** (PCM silence), hold briefly, then hard GPIO mute — hard-zeroing the buffer and hard-cutting GPIO causes clicks.
- Do not leave a 1 kHz PWM constructed “for later” at init; construct only when sounding.

## Sample playback tips (bit-bang DAC)

- Pace with **`time.ticks_us` busy-wait** toward `1e6 / sample_hz`, not only `sleep_us`.
- If the loop falls behind, resync; do not spiral late forever.
- Long `machine.disable_irq()` around a multi-second riff can trip the watchdog — prefer tight per-sample timing without multi-second IRQ off.
- Keep boot riffs short; stream large assets with I2S if quality matters.

## I2S + internal DAC (quality path)

For product audio that must sound better than a beeper square:

1. Investigate continuous buffered playback (I2S writing the internal DAC).
2. Prior art (open source, not vendored): [The-Shreyas-M/ESP32-Synth](https://github.com/The-Shreyas-M/ESP32-Synth) — I2S + internal DAC, dual-core audio task, dithering notes for 8-bit quantization.
3. Record adopt / adapt / reject in the **GCU** PR ambiguity log (product choice). Silico only points here.

Do not copy keypad/Web-UI surfaces into silico; extract only host techniques that every GCU might need.

## Deploy / CDC interaction

- Product apps that set **Ctrl-C as data** own the CDC; `mpremote` cannot enter raw REPL until `repl` door or boot window.
- `silico deploy --verify` uses the REPL and **parks the app loop** — soft-reset so boot entry runs after verify.
- Do not put large binary riffs in hygiene-scanned ways that assume UTF-8 source; deploy as copy-only assets (non-`.py` in `[deploy].core` is skipped by host-import hygiene).

## Agent checklist (audio GCU)

1. Read this file once when the product needs speaker/DAC/I2S.
2. Separate **instrument edges** (PWM, mark-space honest) from **voice/samples** (DAC/I2S).
3. Prove **silence** after stop (scope or ear) before claiming manners.
4. If you burned an hour on a new amp/DAC truth: **extend this file** in the silico PR.

## Friction log (append-only bullets)

- LEDC duty 0 hummed M5-class amps until PWM deinit + GPIO low.
- `sleep_us` DAC loops sounded crunchy; `ticks_us` busy-wait improved riffs.
- Hard-zeroing u8 PCM then GPIO mute clicked; fade to mid (128) then mute is softer.
- Ancient UIFlow images reported language `3.4.0`; never map that to mpy-cross.
