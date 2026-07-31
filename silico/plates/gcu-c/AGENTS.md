# AGENTS.md - C / ESP-IDF GCU

Guidance for AI coding agents in **this product repo** (language=c plate).

## FIRST ACTION (first ship / getting started) — do this before any status dump

When the human says *follow silico getting started* (or first ship / Day 1):

0. **Open the silico spine AGENTS** (local `../silico/AGENTS.md` or raw `https://raw.githubusercontent.com/tig/silico/main/AGENTS.md`). The GitHub README/homepage alone is **not** the agent playbook.
1. **Do not** open with tooling narration, `bedside init`, vendoring `third_party/`, PR strategy, or a start-gate chooser.

```text
# TURN 1 — 0a only: silico welcome, paste skeleton + "reply ok/go", END TURN (no picker)
# TURN 2 — after any short reply: open chooser FIRST (not free-text "shall I open the gate?")
bedside ask --id start-first-ship --prompt "Start first ship on this machine?" --choices yes,adjust --default yes
# host picker: same id/prompt/choices only — never invent Go / Host-only / Look around
```

2. **0b** = structured chooser on the turn after 0a. Do not leave a free-text cliff after orientation. Full silico AGENTS (not a fetch digest). One short question; **yes** / **adjust** only.
3. **Decline / exit 10:** halt writes; short re-gate or stop.
4. **After go:** plate / sibling silico paths for manners pin — not pre-go vendor.

Full playbook: silico root `AGENTS.md` FIRST ACTION.

## Spine

Host path comes from **silico** (https://github.com/tig/silico). Pin as host-only.
Device `firmware/` never imports silico.

This plate uses **ESP-IDF** deploy (`silico deploy` → `idf.py build` + flash), not mpremote file copy.
Host gate is **CMake + CTest**, not pytest (unless you add Python tests separately).

Operator manners: **Bedside** via `bedside.toml` (sibling silico vendor paths). Domain notes: `BEDSIDE.md`.

## Spec quality

If product `spec.md` is way under-specified or contradictory, follow silico root **Spec interview mode** (`silico/knowledge/spec-interview.md`). Interactive path (build while the spec improves; re-run later) is valid. Do not invent domain moat. Product truth is **this** checkout + the operator.

## Host gate

```text
cmake -S host -B build/host
cmake --build build/host --target host_test
silico gate
silico product-path
```

Plate ships `.github/workflows/ci.yml` that on `push` / `pull_request`:
checks out this GCU and **sibling** `tig/silico`, runs **cmake host_test**, then
**`silico gate`** (include hygiene + `[host].gate`). Still run
`silico product-path` locally when claiming a full host path.

## Metal

```text
silico doctor
silico wait-device
silico inspect --port COMx
# confirm board, then:
silico deploy --port COMx
# after operator yes:
silico deploy --port COMx --yes --verify
```

ESP-IDF must be installed (`idf.py` or `IDF_PATH`). First flash and update flash are the same image path.

After deploy, **operator-confirm product face** on the bench (see silico root Stage D1). If this GCU’s face is a **screen**, open silico `knowledge/esprec.md` when **esprec** is ready for optional PNG/GIF agent capture — not a substitute for operator confirm, and not a reason to add QEMU to this GCU’s host gate by default.

## HAL seam

Portable domain under `include/` + `src/` must not include freertos / esp_* / driver headers.
Only stems listed in `[hal].allow_device_headers` (default `hal_board`) may touch device headers.

### Time is int64_t milliseconds

The HAL clock hook is `int64_t now_ms` (see `include/gcu/hal.h`). On ESP32
(ILP32) `long` is **32 bits**: millisecond math in `long`/`int` overflows in
under 10 hours and wraps at ~24.8 days. Host `long` is 64-bit, so host tests
only catch this if they seed the clock past 2^31 — `host/test_time.c` does
exactly that; keep that seed when you extend the domain.

## ESP-IDF environment gotchas

- If the agent/GCU **venv is on PATH ahead of the IDF python env**, `idf.py`
  resolves the wrong interpreter and fails on missing packages. Deactivate or
  strip the venv from PATH before `. $IDF_PATH/export.sh`.
- An existing install is usually recorded in `~/.espressif/idf-env.json` —
  `silico doctor` reads it; check before installing another IDF.
- More: `silico/knowledge/macos-codex-esp-idf.md`.

## Link command surface (identity + escape hatch)

**Boot-print alone is not enough** for `silico inspect` after a greeting or banner scrolls past (#78 / #79). The image **must answer** the host word `identity` (CR/LF framed) with:

```text
fw_name=GCU fw_version=0.0.1
```

Plate `main.c` shows the pattern: print once at boot **and** respond when the host knocks. A boot-print-only app is invisible to inspect as soon as the banner is gone.

`identity`, `repl`, and `reboot` all ship in the plate. The escape hatch is **not optional decoration**: `repl` parks outputs and releases the console so a host can redeploy without hardware gymnastics, and `reboot` parks then hard-resets. A build without the door cannot be reclaimed on a bench.

### Parsing lives in the domain, not in main.c

`gcu_parse_command` / `gcu_handle_command` are in `src/domain.c`; `firmware/main/main.c` only moves bytes. Keep it that way:

1. `silico inspect` knocks **`identity`** and nothing else. Whatever else your product declares is verified by **your** host tests or not at all — so put the surface where a host test can reach it.
2. A dispatcher inside `firmware/` is device-only code, which means "protocol parsing" can never be part of a host-green claim.

`host/test_protocol.c` covers identity, `repl` parking, deferred `reboot`, blank lines, and unknown input failing closed. **Add a row for every command your product spec declares** — including the ones that must be refused. If your spec says the listed commands are the complete surface, do not quietly ship a fourth one (diagnostic capture hooks included).

Outputs your board drives get quieted in the HAL's `park_outputs` — extend it as the product grows a speaker, strips, or actuators. `repl` handing back a console while the product is still singing is a defect.

## Product defaults and host coverage

`silico product-path` proves a host scenario **loads** `[host].product_defaults` — it does not prove your spec's normative behavior is covered. Those are different claims. When the product spec has normative tables (button map, state machine, cycle order, screen layout), give each one a host test; the plate's `host/` files are a **floor to build on, not a ceiling**. Three shipped test files is what the plate happens to need, not what your product needs.

Anything unmeasurable in the spec ("smooth", "comfortable", "a debounce") becomes a number the moment you implement it. Put it in `include/gcu/defaults.h` and tell the operator you chose it — do not let the choice exist only in your head.

## Display HAL granularity (screens)

If the product face is a screen, the HAL's drawing primitives are a performance contract, not a formality. Compose a region into a buffer and **blit it once**; do not render text or glyphs by calling a per-pixel `fill_rect` in a loop. A 5x7 glyph drawn pixel-by-pixel is ~35 SPI transactions (and ~35 allocations if the backend allocates per call) **per character** — a six-row sensor readout at 10 Hz becomes tens of thousands of transactions per second, which is exactly the load that fights an audio DMA feeder and shows up as stutter the operator can hear.

Keep partial paints regional (eye only, banner strip only, value fields only) and reserve full-screen clears for mode changes.
