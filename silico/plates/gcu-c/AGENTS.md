# AGENTS.md - C / ESP-IDF GCU

Guidance for AI coding agents in **this product repo** (language=c plate).

## FIRST ACTION (first ship / getting started) — do this before any status dump

When the human says *follow silico getting started* (or first ship / Day 1):

**Do not** open with tooling narration, `bedside init`, vendoring `third_party/`, PR strategy, or a start-gate chooser.

```text
silico welcome          # 0a orientation source FIRST (read-only; do not block on bedside doctor)
# paste that output as the first operator-facing chat message, then:
bedside ask --id start-first-ship --prompt "Start first ship on this machine?" --choices yes,adjust --default yes
# or host picker (same contract; short prompt only — no Stage A–C essay in the chooser)
```

1. **0a:** Paste/adapt `silico welcome` as your **first** operator-facing chat message. Missing `bedside.toml` is **not** a reason to skip 0a or to `bedside init` before go.
2. **0b:** Only after 0a is in chat. Gate body = one short question. Prefer CLI when it reaches the operator; host picker is sanctioned when stdin cannot — say once.
3. **Decline / exit 10:** halt writes; one short reply; re-gate or stop.
4. **After go:** fix manners pin via plate / sibling silico paths if needed — not a pre-go full vendor into this tree.

Full playbook: https://github.com/tig/silico `AGENTS.md`.

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
