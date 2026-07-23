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

## HAL seam

Portable domain under `include/` + `src/` must not include freertos / esp_* / driver headers.
Only stems listed in `[hal].allow_device_headers` (default `hal_board`) may touch device headers.

## Identity

Boot (or `identity` command) must print:

```text
fw_name=GCU fw_version=0.0.1
```

Escape hatch (`repl` / `reboot`) is a product requirement for reclaim without hard reset when possible.
