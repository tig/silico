# M5-class core host truth (M5GO / Basic / Fire family)

Classic ESP32 M5Stack **Core** boards (M5GO IoT kit, Basic, Fire, …). Pin packs ship as board profile **`m5go`** (`silico board-profile show m5go`). Confirm on the unit in hand — revs differ.

Related: [esp32-audio.md](esp32-audio.md), [esp32-lcd-ips.md](esp32-lcd-ips.md), [m5go-power.md](m5go-power.md), [board-profiles.md](board-profiles.md).

## Product-face candidates (profile m5go)

| Surface | Candidate | Notes |
|---------|-----------|--------|
| Side status strip | GPIO **15** | Often NeoPixel bus; confirm LED count/order |
| Speaker | GPIO **25** | DAC1 / amp; see esp32-audio |
| IPS | **ILI9342C** on **SPI3** | SCLK **18**, MOSI **23**, CS **14**, DC **27**, RST **33**, BL **32** |
| Display flags | invert **ON**, color **BGR** | Wrong flags → washed/inverted colors (see esp32-lcd-ips) |
| Buttons A/B/C | GPIO **39 / 38 / 37** | **Active-low**; external pull-ups on M5 |
| Internal I2C | SDA **21**, SCL **22** | IMU + optional grove on same bus |

### Buttons / ADC-class GPIOs

GPIO **34–39** are input-only and **have no internal pull-ups**. Do not enable `GPIO_PULLUP` on 39/38/37 and expect it to work — rely on the board’s external pull-ups (or add external resistors). Active level is **low** when pressed on stock M5 fronts.

## MPU6886 (not MPU6050)

M5GO-class cores ship **MPU6886** (InvenSense) on the internal I2C bus, not a bare MPU6050.

| Field | Value |
|-------|--------|
| I2C address | **0x68** |
| WHO_AM_I | **0x19** (read register 0x75) |
| Temperature | **`T = raw / 326.8 + 25`** (°C) |

### Footgun: MPU6050 temperature formula

MPU6050 folklore (`raw/340 + 36.53` or similar) is **wrong** on MPU6886 and yields nonsense °C. Always use the **6886** scale above unless you measured a different part.

WHO_AM_I **0x19** confirms 6886-class; do not assume 0x68 means 6050.

## Power

M5GO battery / power button behavior: [m5go-power.md](m5go-power.md).

## first-ship workflow

1. `silico board-profile show m5go` — see candidates (LED, speaker, display, buttons, I2C).
2. Operator-confirm map → `silico board-profile seed m5go --yes` only after yes.
3. Metal acceptance is still operator see/hear of the **product face** (AGENTS Stage D1) — profile seed is not metal done.
