# Throwaway: C-backend serial identity (plan #53)

**Not production. Do not import from `silico` package code. Delete or graduate later.**

## Bench target (this session)

| | |
|--|--|
| Port | **COM8** |
| Operator ID | SparkFun **Artemis ATP** (Ambiq Apollo3 Blue) |
| Bridge | CH340 (`1A86:7523`) |
| Plan role | Exercise the **language-agnostic serial identity path** (plan Phase 3 precursor) |

### Honest limits

- Artemis ATP is **not** ESP32. **ESP-IDF / esptool cannot target this board.**
- No MicroPython REPL on COM8 (confirmed: `mpremote` cannot enter raw REPL).
- Boot capture at 115200 / 460800 / 921600 / 57600 with DTR/RTS toggle yields no ASCII identity — board is silent or binary-only at those rates.
- Useful for: port open, reset edges, fail-closed inspect copy, identity **parser** unit tests.
- Not useful for: IDF flash, chip detect, mpy deploy.

ESP32-class metal proof still needs COM7 (CH9102 / M5GO candidate) or a real ESP32-S3.

## What this experiments

Precursor to plan §4.3 (inspect without mpremote):

1. Open an explicit `--port` (never blind auto-pick on CH340 benches).
2. Optional DTR/RTS reset.
3. Knock: newline + `identity\n`.
4. Parse `fw_name=… fw_version=…` (key=value tokens).
5. Compare to expected product identity when provided.
6. Exit codes agents can use: `0` match/found, `10` no identity, `30` port/tool error.

## Run

```text
# From repo root (editable silico not required)
py -3 experiments/c_backend/probe.py --port COM8
py -3 experiments/c_backend/probe.py --port COM8 --expect-name XUSSC --expect-version 0.0.1

# Parser self-check (no hardware)
py -3 experiments/c_backend/probe.py --self-test
```

## Graduate later

When this shape is proven on a talking C/ESP image, move parser + serial knock into `silico/` (shared by inspect + deploy verify) and delete this tree.
