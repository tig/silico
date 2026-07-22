# ESP32 USB-serial (host knowledge)

Classic ESP32 + CH9102/CP210x USB-UART. After first-flash, tools use mpremote on that COM.

## Serial readiness ladder (MicroPython product apps)

Do **not** skip steps. Host gate green ≠ duplex OK.

1. `silico inspect --port COMx` — raw REPL works (stock or known-good).
2. Deploy app **without** `micropython.kbd_intr(-1)` (tool interrupt still works).
3. Prove **round-trip**: host sends a line, device answers (not TX-only telem/identity).
4. Only then: Ctrl-C-is-data + product `repl`/`reboot` door; prove `repl` restores mpremote.
5. Claim metal only after operator-observable product face (AGENTS Phase D1).

**Anti-pattern:** `kbd_intr(-1)` + unproven `serial_read` → TX works, tools locked, `repl` dead → full erase (#62).

## Do not thrash

If inspect/deploy says app owns console / door stayed shut:

- **Do not** redeploy in a loop.
- Files may already be on device.
- Recover **once** (first-flash cookbook), park stock MicroPython, fix duplex on host, then redeploy.

## Footguns

| Footgun | Why |
|---------|-----|
| `machine.UART(0)` while REPL owns console | Often `uart_driver_install API first`; does not fix RX |
| Identity/telem TX only | Proves outbound CDC, not host→device RX |
| Deploy `--verify` then soft-reset into deaf app | Verify used REPL; app may never hear host (#49 race) |

## Lockout recovery (once)

```text
# ESP32 classic
esptool --chip esp32 --port COMx erase-flash
esptool --chip esp32 --port COMx write-flash -z 0x1000 ESP32_GENERIC-<ver>.bin
silico inspect --port COMx
# expect REPL; stock boot.py only — stop; no product redeploy until step 3 above
```

RP2040: UF2 path in [first-flash.md](first-flash.md). Firmware URLs: same file.
