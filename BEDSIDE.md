# BEDSIDE.md (silico metal domain notes only)

This file is **not** a fork of the Bedside principles.

| Need | Open once |
|------|-----------|
| Portable manners (normative) | `third_party/bedside/contract` (pin: `bedside.toml`) |
| Silico Day 1 / CLI / plate | root `AGENTS.md` |
| First-flash detail (UF2 / esptool) | `silico/knowledge/first-flash.md` |
| ESP32 USB duplex / console lockout | `silico/knowledge/esp32-usb-serial.md` |
| ESP32 audio / DAC / PWM silence | `silico/knowledge/esp32-audio.md` |
| This file | metal-host glossary only — do **not** also reload the full contract if AGENTS already pinned it |

## Operator language (pointer)

Plain-language orientation, **first-use term definitions**, and **why + where-we-are** on big steps live in root **AGENTS.md** → *Operator language (silico domain)*. This file stays metal glossary only — do not soft-fork Bedside principles here.

When prompting plug-USB, first-flash, confirm-board, or confirm-deploy: always state **why** the step is needed and **where** Day 1 is (host done vs metal still open).

Before deploy / soft-reset / any act that may **surprise** (loud or long tone, music, bright LEDs, motion): **announce** what will happen and roughly how long — plain agent output is enough; not always a new confirm gate. See root **AGENTS.md** → *Announce surprising metal effects*.

## Metal first-run (domain pack)

Host tools and Day-1 **phase order** live in **AGENTS.md**. Metal-specific once-only path:

1. Data USB cable (not charge-only).
2. Long `silico wait-device` (agent polls; human does not announce plug-in).
3. `silico inspect --port COMx` proves **modern** REPL, **or** first-flash MicroPython **once**:
   - **UF2** (RP2040-class): BOOT+RESET → mass storage → copy `.uf2`.
   - **esptool** (classic ESP32-class): erase + write `ESP32_GENERIC` (or board variant) — see `silico/knowledge/first-flash.md`.
4. Operator confirms this port is the product board before any write (`bedside ask --id confirm-board`, recommended default **no** if unsure).
5. Deploy overwrite only after `bedside ask --id confirm-deploy` (or host UI same contract).
6. **Before write/reset:** clearly tell the operator what the board may do after boot (tones, LEDs, motion, duration) — especially audio products. Permission to overwrite is not a license to startle.
7. After `--verify`, **soft-reset again** so the product boot entry runs (verify parks the app loop).
8. **Operator-observable good:** confirm the human can **see or hear** the documented **product face** for **this** product board (not only `FW_VERSION` over REPL). Always say **product face**, never bare “face.” Plate generic LED on the wrong pin is not acceptance.
9. **Pin / product face mismatch → ask first:** if GPIO, LED, or audio that makes up the product face is unclear vs product docs/board, **stop and clarify with the operator** (`bedside ask` / host picker) before assuming, filing-only, or advancing phases. Then fix → redeploy → re-confirm observe.
10. App updates after first-flash: no re-teaching UF2/esptool.

Do **not** stop Day 1 after host gate green unless the operator explicitly defers metal.  
Do **not** claim “on the metal” while the product face is unproven or only tracked as an open issue.  
Do **not** monologue HW confusion without asking the operator to clarify.  
Do **not** invent short forms of lexicon terms (bare “face” for product face).  
Do **not** start surprising audio/motion without a clear forewarning in agent output.

## Scary surfaces (metal glossary)

| Surface | Plain language |
|---------|----------------|
| USB serial / COM | Prefer explicit `COMx`; demote CH340 adapters and Debug Probe; ESP-class CDC (CH9102, CP210x) may score as candidates — still confirm identity |
| First-flash | UF2 **or** esptool once; never apply mpy pins from language version alone |
| Deploy overwrite | Inspect first; write only with operator yes (`silico deploy --port COMx --yes`). MicroPython: usually `[deploy].core` files. **C / ESP-IDF:** full app image (`idf.py build` + flash). **Announce** post-boot product face (sound/light/motion) before write/reset |
| C image identity | `language = c`: inspect knocks serial for `fw_name=… fw_version=…` (no mpremote REPL) |
| Surprising audio / motion | Loud or long tones, music, actuators: forewarn in plain language before the act — not only after |
| Board identity | High score is a hint; `bedside ask --id confirm-board` (or host picker) |
| Physical plug / BOOT | `bedside step --id …` one instruction + confirm in their words |
| After reset | Port may re-enumerate; re-discover before reuse |
| Unknown board content | `silico pull <dir> --port COMx` before overwrite; `--prune` when orphans matter |
| Running app CDC | App may treat Ctrl-C as data; open product `repl` door or catch boot window before mpremote write |
| Console lockout | Door dead after `kbd_intr(-1)` + broken RX: **do not thrash deploy** — recover once (first-flash erase/UF2), park stock MP; see `esp32-usb-serial.md` (#62) |
| Deploy verify | Uses REPL; **parks the product loop** — soft-reset so main runs; TX after reset ≠ duplex |
| Running app CDC (read-only) | `silico monitor --port COMx` (does not Ctrl-C the loop) |

## Day-2 leave-behind (metal)

MicroPython plate:

```text
pytest -q
silico deploy --port COMx --yes --verify --reset
# soft-reset once more if the product face / app loop is not running
```

C / ESP-IDF plate (`silico scaffold . --plate gcu-c`):

```text
cmake -S host -B build/host && cmake --build build/host --target test
silico deploy --port COMx --yes --verify
```

Requires ESP-IDF (`idf.py` or `IDF_PATH`). First flash and update flash are the same image path.

Good: host gate green; device `FW_VERSION` matches host; **operator-confirmed product face** (LED/status/audio for this product; silence after stop if the product has a speaker). Version match alone is not “good.”

## Customer 0 → tig/bedside

Portable manners gaps (contract, surface, `bedside` CLI, eval): file **tig/bedside**, do not soft-fork principles here.
Metal/host-spine gaps: fix **tig/silico** (including `silico/knowledge/` for board caps).
