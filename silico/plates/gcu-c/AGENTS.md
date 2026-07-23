# AGENTS.md - C / ESP-IDF GCU

Guidance for AI coding agents in **this product repo** (language=c plate).

## FIRST ACTION (first ship / getting started) — do this before any status dump

When the human says *follow silico getting started* (or first ship / Day 1):

**Do not** open with tooling narration, COM folklore, PR strategy, or a start-gate chooser.

```text
bedside doctor          # if fail: fix bedside.toml paths / pip install -e ../silico/third_party/bedside — do not invent a parallel manners path
silico welcome          # orientation source (read-only)
```

1. **0a:** Paste/adapt `silico welcome` output as your **first** operator-facing chat message (minimal adapt only). That skeleton is the orientation — do not hand-build a multi-section status report instead.
2. **0b:** Only after 0a is in chat, open the start gate: `bedside ask --id start-first-ship --prompt "Start first ship on this machine?" --choices yes,adjust --default yes` **or** the host structured picker under the **same contract** (short prompt, recommended first, decline = halt). Prefer the CLI when it can reach the operator; when stdin is unreachable in the agent harness, the host picker is the **sanctioned** shell — say once that you are using it.
3. **Decline / exit 10:** halt writes; one short reply; re-gate or stop. Do not commit/push/scaffold past a no.

Full playbook (stages A–F, metal rules): https://github.com/tig/silico `AGENTS.md`. This file does not soft-fork it.

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
