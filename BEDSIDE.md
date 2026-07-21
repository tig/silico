# BEDSIDE.md (silico metal domain notes only)

This file is **not** a fork of the Bedside principles.

| Need | Open once |
|------|-----------|
| Portable manners (normative) | `third_party/bedside/contract` (pin: `bedside.toml`) |
| Silico Day 1 / CLI / plate | root `AGENTS.md` |
| First-flash detail (UF2 / esptool) | `silico/knowledge/first-flash.md` |
| ESP32 audio / DAC / PWM silence | `silico/knowledge/esp32-audio.md` |
| This file | metal-host glossary only — do **not** also reload the full contract if AGENTS already pinned it |

## Metal first-run (domain pack)

Host tools and Day-1 **phase order** live in **AGENTS.md**. Metal-specific once-only path:

1. Data USB cable (not charge-only).
2. Long `silico wait-device` (agent polls; human does not announce plug-in).
3. `silico inspect --port COMx` proves **modern** REPL, **or** first-flash MicroPython **once**:
   - **UF2** (RP2040-class): BOOT+RESET → mass storage → copy `.uf2`.
   - **esptool** (classic ESP32-class): erase + write `ESP32_GENERIC` (or board variant) — see `silico/knowledge/first-flash.md`.
4. Operator confirms this port is the product board before any write (`bedside ask --id confirm-board`, recommended default **no** if unsure).
5. Deploy overwrite only after `bedside ask --id confirm-deploy` (or host UI same contract).
6. After `--verify`, **soft-reset again** so the product boot entry runs (verify parks the app loop).
7. App updates after first-flash: no re-teaching UF2/esptool.

Do **not** stop Day 1 after host gate green unless the operator explicitly defers metal.

## Scary surfaces (metal glossary)

| Surface | Plain language |
|---------|----------------|
| USB serial / COM | Prefer explicit `COMx`; demote CH340 adapters and Debug Probe; ESP-class CDC (CH9102, CP210x) may score as candidates — still confirm identity |
| First-flash | UF2 **or** esptool once; never apply mpy pins from language version alone |
| Deploy overwrite | Inspect first; write only with operator yes (`silico deploy --port COMx --yes`, usually `[deploy].core`) |
| Board identity | High score is a hint; `bedside ask --id confirm-board` (or host picker) |
| Physical plug / BOOT | `bedside step --id …` one instruction + confirm in their words |
| After reset | Port may re-enumerate; re-discover before reuse |
| Unknown board content | `silico pull <dir> --port COMx` before overwrite; `--prune` when orphans matter |
| Running app CDC | App may treat Ctrl-C as data; open product `repl` door or catch boot window before mpremote write |
| Deploy verify | Uses REPL; **parks the product loop** — soft-reset so main runs |
| Running app CDC (read-only) | `silico monitor --port COMx` (does not Ctrl-C the loop) |

## Day-2 leave-behind (metal)

```text
pytest -q
silico deploy --port COMx --yes --verify --reset
# soft-reset once more if the app face/loop is not running
```

Good: host gate green; device `FW_VERSION` matches host; documented LED/status (and silence after stop if the product has a speaker).

## Customer 0 → tig/bedside

Portable manners gaps (contract, surface, `bedside` CLI, eval): file **tig/bedside**, do not soft-fork principles here.
Metal/host-spine gaps: fix **tig/silico** (including `silico/knowledge/` for board caps).
