# ESP32 USB-serial (host knowledge)

Classic ESP32 + CH9102/CP210x USB-UART. After first-flash, tools use mpremote on that COM.

## Serial readiness ladder (MicroPython product apps)

Do **not** skip steps. Host gate green ≠ duplex OK.

1. `silico inspect --port COMx` — raw REPL works (stock or known-good).
2. Deploy app **without** `micropython.kbd_intr(-1)` (tool interrupt still works).
3. Prove **round-trip**: host sends a line, device answers (not TX-only telem/identity).
4. Only then: Ctrl-C-is-data + product `repl`/`reboot` door; prove `repl` restores mpremote.
5. Claim metal only after operator-observable product face (AGENTS Stage D1).

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
| DTR/RTS pulse before C identity knock on CH9102 | Resets into ROM / download; `silico inspect` captures 0 bytes while bare pyserial (dtr=rts=False + `identity`) works (#78) |

## C / ESP-IDF identity (language=c)

`silico inspect` uses serial knock (`identity` + CR/LF), not mpremote.

1. Open with **DTR/RTS deasserted** and knock **without** a reset pulse first (CH9102 / M5GO).
2. **Re-knock** on a short interval for the full listen window so a boot greeting cannot bury a one-shot line (#79).
3. If no `fw_name=` line, optional pulse + boot wait + knock again.
4. Capture window defaults longer than a single boot greeting (~3s).

**Product requirement:** the C image must **answer** `identity` on the link, not only print at boot. Boot-print-only becomes invisible the moment the banner scrolls past. Plate `gcu-c` main shows both: boot line + knock responder.

Manual check when inspect is empty but the app is alive: open the COM with dtr/rts false, write `identity` and a newline, read the response.

## Lockout recovery (once)

```text
# ESP32 classic
esptool --chip esp32 --port COMx erase-flash
esptool --chip esp32 --port COMx write-flash -z 0x1000 ESP32_GENERIC-<ver>.bin
silico inspect --port COMx
# expect REPL; stock boot.py only — stop; no product redeploy until step 3 above
```

RP2040: UF2 path in [first-flash.md](first-flash.md). Firmware URLs: same file.
