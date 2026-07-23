# ESP32 audio on the host path (self-improving)

Generic board/runtime notes for GCUs that **play tones, riffs, or instrument-like audio** on classic ESP32 (internal DAC and/or PWM) under **MicroPython**. Not product song lists or vertical moats.

When you learn a new host truth on a bench, **add a bullet here** (or a sibling file + INDEX row). Prefer **measure on metal** over folklore; self-report is not measurement.

## Hardware map (classic ESP32)

| Resource | Typical pins | Use |
|----------|--------------|-----|
| DAC1 | GPIO **25** | 8-bit analog out; often wired to on-board speaker amp |
| DAC2 | GPIO **26** | Second DAC; also common for Grove “signal” / PWM |
| LEDC PWM | most GPIOs | Square / edge trains; fine for tach; harsh for “music” |
| I2S → internal DAC | 25/26 via I2S peripheral | Better sample streams (see prior art below) |

Board schematics differ (amp enable, AC couple). Always ground in the product’s `parts.toml` / board docs before claiming metal audio.

**M5-class cores (M5GO / Basic / Fire family):** on-board speaker is commonly driven from **GPIO25** through a small amp. Same pin is often also used for square-wave “voice” via LEDC. Treat DAC and PWM as **one pin, two modes** with a one-way trap (below).

**first-ship pin pack:** prefer packaged profile **`m5go`** (`silico board-profile show m5go`; side strip **15** + speaker **25**) over inventing pins in chat. Seed candidates: `silico board-profile seed m5go` (see [board-profiles.md](board-profiles.md)).

## Operator forewarning (manners)

Before deploy/reset that may play a boot riff, long tone, or other non-trivial audio: **state it in agent chat first** (what, how long, what “done” sounds like). See silico root `AGENTS.md` → *Announce surprising metal effects*. Permission to overwrite firmware is not permission to startle.

## Tones vs samples

| Need | Prefer | Avoid |
|------|--------|--------|
| Tach / edge honesty to a DUT | Hardware **PWM** with true `duty_pct` | Encoding “volume” by thinning duty (sounds like hash) |
| Short UI chirps | PWM or DAC square with clean park | Leaving LEDC at duty 0 |
| Boot riff / PCM (u8 mono) | Long-lived **DAC** sample loop, or **I2S+DAC** | `time.sleep_us` alone for pacing (jitter → distortion) |
| Polyphonic / soft synth | I2S + FreeRTOS-style continuous buffer | Bit-banging DAC from the UI tick |

## Critical: MicroPython `machine.DAC` lifecycle (measured)

Bench-proven on MicroPython **v1.28 ESP32_GENERIC** (classic ESP32, speaker on GPIO25). Treat as default host truth until a later build measures otherwise.

### What fails

| Sequence | Result |
|----------|--------|
| Hard reset → first `DAC(Pin(25))` | **OK** |
| First DAC `deinit()` / drop / GPIO remux → second `DAC(Pin(25))` | **`OSError` / `ESP_ERR_INVALID_STATE` (-259)** until **hard** reset |
| PWM (LEDC) on GPIO25 (even after PWM `deinit`) → later `DAC(Pin(25))` | **FAIL** for the rest of that boot |
| Soft reboot alone after the above | **Does not** restore DAC open |

MicroPython call shape is `from machine import DAC, Pin` then `DAC(Pin(25))` (or the board speaker pin). Tables below use that form; do not write bare `DAC(25)`.

So: **the first successful DAC open is precious.** Releasing the DAC object or taking the pin for PWM is a one-way trip to “PWM-only or silence” until RTS/en hard reset (or power cycle that hard-resets the chip).

Related ecosystem reports exist around ESP-IDF DAC re-init / MicroPython DAC rebind; do not rely on “just open it again” without measuring **your** image.

### What works (product pattern)

1. **Open DAC once** after boot when first sample audio is needed.
2. **Keep the object for the app lifetime** while you still care about PCM quality.
3. **Soft-park silence:** `dac.write(0)` (or hold u8 mid then park — see fade below). Do **not** `deinit()`, do **not** rebind the pin as digital out, do **not** call emergency GPIO remux that abandons the DAC session.
4. **Hard-kill** (PWM teardown + abandon DAC) only when you **intentionally** need square-wave LEDC on that pin and accept losing PCM for this boot.
5. Prefer **hard reset** (esptool RTS / power) over soft reboot when debugging “DAC won’t open.”

### Anti-patterns (sound bad or brick the channel)

- Open DAC for boot riff → deinit “to free the pin” → try to reopen for a longer song later.
- Play PCM → `emergency_silence()` that forces GPIO OUT low / remux → later song is PWM mush or silent.
- Use PWM as a “temporary” speaker path on GPIO25, then expect DAC PCM quality afterward.
- Assume soft reboot fixes DAC state.

## Silence is hard (bench-proven)

- **PWM duty 0 is not silence** on many ESP32 + amp boards — the LEDC channel still drives the amp. **Deinit PWM** and rebind the pin as **GPIO OUT low** (or board-documented idle) when you are in PWM mode.
- Dropping a Python `DAC` reference may **not** unmux the pin. Prefer an explicit quiet write while **keeping** the object if you will play samples again.
- After sample playback, avoid a cliff:
  1. Ease samples toward **u8 mid (128)** (digital silence for unsigned PCM),
  2. Hold mid briefly,
  3. Optionally ramp mid → 0,
  4. Soft-park the DAC (`write(0)`) **without** destroying the session if more PCM will follow this boot.
- Hard-zeroing the buffer and hard-cutting GPIO causes **clicks**.
- Do not leave a 1 kHz PWM constructed “for later” at init; construct only when sounding.

## Smooth PCM / “music” on MicroPython (bit-bang DAC)

This path is good enough for short boot riffs and simple mono songs when I2S is not wired. It is not studio hi-fi.

### Format

- **Unsigned 8-bit mono** PCM is the simple fit for `DAC.write(0..255)`.
- Sample rates around **8–11.025 kHz** are realistic for bit-bang loops on ESP32 MicroPython; higher rates drop samples and sound crunchy.
- **Stream from the filesystem** (`open` + chunked `read`) for multi-minute tracks. Do not load multi‑MB songs into RAM.

### Pacing

- Pace with **`time.ticks_us` busy-wait**, not only `time.sleep_us`.
- **Do not floor-divide a fixed period and leave it.** Rates like 11_025 Hz do not divide 1_000_000 evenly.
  - Bad: `period = 1_000_000 // sample_hz` → at 11025 Hz this is always **90 µs** (~11111 Hz), about **0.78% fast** (audibly sharp; track finishes early).
  - OK short riff (integer nearest µs): `period = (1_000_000 + sample_hz // 2) // sample_hz` → **91 µs** at 11025 Hz (still slightly off long-term).
  - **Preferred long-term pitch:** Bresenham-style **remainder accumulator** so average sample period is exactly `1_000_000 / sample_hz` µs:

```text
base = 1_000_000 // sample_hz          # floor µs between samples
rem  = 1_000_000 %  sample_hz          # leftover that must be distributed
err  = 0
for each sample:
    period = base
    err += rem
    if err >= sample_hz:
        period += 1
        err -= sample_hz
    wait period µs (ticks_us deadline)
```

    At 11025 Hz: `base=90`, `rem=10000`; most steps are 90 µs, some are 91 µs, average = 1e6/11025.
- Maintain a `t_next` deadline: write sample → `t_next += period` → spin while `ticks_diff(t_next, now) > 0`.
- If the loop falls behind (`ticks_diff` largely negative), **resync** `t_next` to now; do not spiral late forever (prevents multi-second “catch-up mute” then a dump of late samples).
- Long `machine.disable_irq()` around multi-second audio can trip the watchdog — prefer tight per-sample timing without multi-second IRQ off.

### Start and end shape

- Lead-in: a few mid (128) samples before the first real sample reduces pop-in.
- End of a one-shot riff: **fade toward mid** (linear is OK; cubic-ish ease on the residual is softer), **hold mid**, optional ramp to 0, then soft-park DAC.
- Mid-stream song chunks: **do not** fade out every chunk; only fade when stopping or finishing the track.
- Pause/resume: keep a **byte offset** into the file; pause must not restart from zero unless the product says so.

### Cooperative multi-tasking while streaming

- A pure busy-wait sample loop monopolizes the core: face animation and serial will stall. That may be acceptable for a **short** boot riff.
- For longer tracks, **yield often enough** to: poll pause/stop (and product UI buttons), and **service the USB serial link** (at least `identity` / `repl` / `reboot`) unless the **product spec** explicitly allows a deferred escape hatch. Multi-minute deafness to the link is a product defect when the spec requires mid-play `repl`.
- Document the product UI honestly (Now Playing while audio owns most of the loop is fine if inputs and link still get slices).

### Amp / bus coupling

- Aggressive **NeoPixel / SK6812 bit-bang**, heavy SPI LCD traffic, or other busy loops **during** sample write increase jitter and can couple into the amp as buzz.
- Prefer: finish or pause flashy LED updates around critical PCM; use **static** side LED frames while playing long audio if the product allows.
- Partial LCD updates (banner strip, eye only) reduce SPI thrash vs full-frame clears every animation tick.

### PWM fallback

- If DAC open fails, a PWM “PCM” approximation (duty modulated by sample) may be a last resort. It sounds worse.
- Using PWM fallback on the **same** pin as DAC **poisons** further DAC opens for that boot (see lifecycle). Prefer failing closed or requiring hard reset over silently degrading forever without telling the link/operator.

## I2S + internal DAC (quality path)

For product audio that must sound better than bit-bang DAC:

1. Investigate continuous buffered playback (I2S writing the internal DAC).
2. Prior art (open source, not vendored): [The-Shreyas-M/ESP32-Synth](https://github.com/The-Shreyas-M/ESP32-Synth) — I2S + internal DAC, dual-core audio task, dithering notes for 8-bit quantization.
3. Record adopt / adapt / reject in the **GCU** PR ambiguity log (product choice). Silico only points here.

Do not copy keypad/Web-UI surfaces into silico; extract only host techniques that every GCU might need.

## Deploy / CDC interaction

- Product apps that set **Ctrl-C as data** own the CDC; `mpremote` cannot enter raw REPL until `repl` door or boot window.
- `silico deploy --verify` uses the REPL and **parks the app loop** — soft-reset so boot entry runs after verify.
- Do not put large binary riffs in hygiene-scanned ways that assume UTF-8 source; deploy as copy-only assets (non-`.py` in `[deploy].core` is skipped by host-import hygiene).
- Large audio assets: host-side upload scripts (chunked / base64) beat a single fragile `mpremote cp` when links drop mid-multi‑MB copy.

## Agent checklist (audio GCU)

1. Read this file once when the product needs speaker/DAC/I2S.
2. Separate **instrument edges** (PWM, mark-space honest) from **voice/samples** (DAC/I2S).
3. Plan the **DAC session**: one open, soft-park, hard-kill only when PWM must own the pin.
4. Prove **silence** after stop (scope or ear) before claiming manners — no click, no LEDC hum.
5. Prove **second play** after the first riff without hard reset (catches accidental deinit).
6. If you burned an hour on a new amp/DAC truth: **extend this file** in a silico PR.

## Measure recipe (when the board disagrees)

1. Hard-reset the chip (esptool RTS or power).
2. From a clean REPL (product parked), try `DAC(Pin(25))` / board speaker pin once — expect OK.
3. `deinit` or rebind, open again — expect INVALID_STATE on many images.
4. Hard-reset, open DAC, play a short mid-level buffer with `ticks_us` pacing; ear-check.
5. Soft-park (`write(0)`), play again — expect OK if session kept.
6. Only then try PWM on the same pin; document whether DAC returns.

Keep results in the GCU (script + notes). Promote durable bullets **here**.

## Friction log (append-only bullets)

- LEDC duty 0 hummed M5-class amps until PWM deinit + GPIO low.
- `sleep_us` DAC loops sounded crunchy; `ticks_us` busy-wait improved riffs.
- Hard-zeroing u8 PCM then GPIO mute clicked; fade to mid (128), hold, ramp, then soft-park is softer.
- Ancient UIFlow images reported language `3.4.0`; never map that to mpy-cross.
- MicroPython ESP32: first `DAC(Pin(25))` after hard reset OK; reopen after deinit/GPIO remux/PWM → `ESP_ERR_INVALID_STATE` until hard reset; soft reboot does not restore (measured 2026-07, MP 1.28 GENERIC).
- Keeping one DAC session across boot riff + later full-song stream restored “boot riff quality” for the longer track; reopening failed closed or fell back to harsh PWM.
- `emergency_silence` / GPIO remux after a soft-parked riff reintroduced a harsh cutoff and killed DAC reopen for the song path.
- NeoPixel side-strip updates interleaved with DAC sample loops coupled noise into the amp; static sides during long PCM helped.
- Streaming u8 mono from flash in ~1 KiB chunks with button polls between/inside chunks allows pause without loading the whole file into RAM.
- `period = 1_000_000 // 11025` floors to 90 µs (~0.78% fast); use rounded period or remainder-accumulator (`base` + distribute `1e6 % hz`) for correct pitch/duration.
