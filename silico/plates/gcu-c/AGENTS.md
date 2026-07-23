# AGENTS.md - C / ESP-IDF GCU

Guidance for AI coding agents in **this product repo** (language=c plate).

## Spine

Host path comes from **silico** (https://github.com/tig/silico). Pin as host-only.
Device `firmware/` never imports silico.

Start: *See https://github.com/tig/silico. Follow the getting started instructions for agents.*

This plate uses **ESP-IDF** deploy (`silico deploy` → `idf.py build` + flash), not mpremote file copy.
Host gate is **CMake + CTest**, not pytest (unless you add Python tests separately).

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
