# First-flash MicroPython (host knowledge)

After first-flash, deploys are mpremote over USB CDC for all supported boards.

## Detect which path

| Signal | Path |
|--------|------|
| `silico inspect --port COMx` talks REPL; modern MicroPython (`1.20+`) | No first-flash; deploy app |
| Mass-storage volume `RPI-RP2` (or similar) after BOOT+RESET | **UF2** drag-and-drop once |
| ESP32 talks serial but REPL is missing / UIFlow-era / ancient MP (`1.12`-class) | **esptool** erase + write once |
| App owns CDC (cannot enter raw REPL; Ctrl-C is data) | Knock `repl` / boot window. If door dead: **stop thrashing deploy** — recover once via erase+write (ESP) or UF2 (RP2040), park stock MP. See [esp32-usb-serial.md](esp32-usb-serial.md) (#62) |

## UF2 (RP2040-class)

1. Operator holds BOOT, taps RESET → `RPI-RP2` volume.
2. Copy the board’s MicroPython `.uf2` (prefer `silico first-flash` below for byte progress).
3. Re-enumerate COM; `silico inspect --port COMx`.

```text
# After BOOT+RESET → volume mounted (e.g. E:\)
silico first-flash firmware.uf2 --uf2-dest E:/firmware.uf2
silico first-flash firmware.uf2 --uf2-dest E:/firmware.uf2 --yes
# streams: PROGRESS [uf2-copy] N% (written / total)
```

## esptool (ESP32-class classic)

Prefer the silico verb so **progress streams** to the operator (`PROGRESS [esptool] …` percentages):

```text
# dry plan (no write)
silico first-flash ESP32_GENERIC-<date>-vX.Y.Z.bin --port COMx
# after operator confirm board + image:
silico first-flash ESP32_GENERIC-<date>-vX.Y.Z.bin --port COMx --yes
# variants:
silico first-flash image.bin --port COMx --chip esp32s3 --offset 0x0 --yes
silico first-flash image.bin --port COMx --no-erase --yes   # skip erase-flash
```

Manual equivalent (if you must):

```text
esptool --chip esp32 --port COMx erase-flash
esptool --chip esp32 --port COMx write-flash -z 0x1000 ESP32_GENERIC-<date>-vX.Y.Z.bin
```

- Firmware: [MicroPython ESP32_GENERIC downloads](https://micropython.org/download/ESP32_GENERIC/) (or the matching board variant).
- Install host tool: `python -m pip install esptool`.
- After flash: hard reset; `silico inspect --port COMx`; only then `--apply-mpy-pin`.

Do **not** apply mpy-cross pins from language version alone (e.g. `3.4.0` on old images).

Same erase+write is the **lockout recovery** when product app owns CDC and `repl` never opens — once, then park stock; do not redeploy product until duplex is proven ([esp32-usb-serial.md](esp32-usb-serial.md)).

## After first-flash

Same for all boards:

```text
silico inspect --port COMx --apply-mpy-pin
silico deploy --port COMx   # dry plan (lists sizes + PROGRESS stages)
# operator confirm → announce surprising product face effects if any →
silico deploy --port COMx --yes --verify --reset
# live: PROGRESS [write] i/n name (size), then reset / verify stages
# soft-reset again if the product face / app loop is not running after verify
```
