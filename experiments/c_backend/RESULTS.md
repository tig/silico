# Bench results — COM8 Artemis ATP

**When:** 2026-07-21  
**Host:** Windows, pyserial 3.5, silico worktree  
**Branch:** `exp/c-backend-serial-identity`

## Inventory

| Port | Bridge | Operator |
|------|--------|----------|
| COM8 | CH340 `1A86:7523` | Artemis ATP (Apollo3) — this experiment |
| COM7 | CH9102 `1A86:55D4` | ESP32 / M5GO candidate (not used here) |
| COM3 | CH340 `1A86:7523` | unknown |

## Commands

```text
py -3 experiments/c_backend/probe.py --self-test   # exit 0
py -3 experiments/c_backend/probe.py --port COM8   # exit 10 (no identity)
```

## Findings

1. **Self-test:** parser accepts `fw_name=… fw_version=…` and two-line name/version; rejects noise.
2. **COM8 open:** works; DTR/RTS pulse runs without error.
3. **Capture @ 115200:** 1 garbage byte (`0xFC` / `0xFE`); no ASCII.
4. **Capture @ 921600:** 7 binary bytes (`00 60 06 66 78 e6 e0`); no identity line (likely bootloader noise, not protocol).
5. **mpremote** (earlier session): cannot enter raw REPL — not MicroPython.
6. **ESP-IDF / esptool:** not installed on host; would not apply to Apollo3 even if present.

## Implication for plan #53

| Plan slice | Status on COM8 |
|------------|----------------|
| Explicit `--port`, no blind auto-pick | Exercised |
| Serial identity knock (no mpremote) | Exercised; fail-closed exit 10 |
| Identity parser | Unit-proven |
| IDF deploy / chip flash | **Blocked** — wrong MCU class |
| Full Day 1 C GCU | Needs ESP32-class board (e.g. COM7) + IDF install |

## Next throwaway (suggested)

1. Install esptool; dry-run chip detect on **COM7** (ESP candidate), not COM8.
2. Or graduate `identity.py` into `silico/` with host tests once an ESP image prints identity.
3. Host-only Phase 1 (`[runtime].language`) needs no board — can land in parallel.
