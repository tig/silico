# ESP32-S3 1.8″ Touch AMOLED (Waveshare / Amazon class)

**Board class:** ESP32-S3-Touch-AMOLED-1.8 (e.g. Amazon ASIN B0F242GFHK, Waveshare ESP32-S3-Touch-AMOLED-1.8).  
**Native panel:** **368 × 448** QSPI AMOLED, capacitive touch, **8 MB OPI PSRAM**, **16 MB** flash.  
**Product UI often:** landscape **448 × 368** with USB + hard keys on the **top** edge (rotate content, not the panel timings).

Open this file when bringing up a GCU **product face** on this board class. Do not invent pin maps from chat.

## Controllers (read this first)

Driver selection is by **hardware revision**, not by the retail listing name alone. Product pages often say “SH8601” for the whole SKU family; that is not enough to pick the init path.

| Revision signal | How to detect | Driver / notes |
|-----------------|---------------|----------------|
| **V2** (newer) | I2C probe **0x15** (CST816) responds | **CO5300** over QSPI + optional `x_gap = 0x10`. Port Waveshare **`13_display_colorbar`**: `espressif/esp_lcd_co5300` + Waveshare init table (works on IDF **5.3.2**). |
| **Original** | 0x15 absent; touch often **FT3168** at another address | **SH8601** path (`waveshare/esp_lcd_sh8601` or equivalent). Do **not** point original units at the V2 CO5300 colorbar sequence. |

**Field lesson (first metal, 2026-07, V2-class unit):**  
- On units that match the V2 probe, `waveshare/esp_lcd_sh8601` can report “create success” and still leave a **black** panel.  
- On that revision, the **CO5300** colorbar path lights the panel; SH8601 alone is the wrong fallback.  
- Newer Waveshare ESP-IDF examples ask for IDF **≥ 5.5** for BSP packages; the **CO5300 component alone** is enough for a custom GCU on 5.3.x when the unit is V2.

IDF component when the unit is V2 / CO5300 (pinned by product):

```text
espressif/esp_lcd_co5300: "^1.0.0"   # resolved 1.0.2 on IDF 5.3.2
```

Do **not** require IDF 5.5 solely to light the panel.  
Do **not** apply the V2 CO5300 sequence to original / FT3168 units — keep those on **SH8601**.

## Pins (display QSPI)

| Signal | GPIO |
|--------|------|
| CS | 12 |
| PCLK / SCLK | 11 |
| D0 | 4 |
| D1 | 5 |
| D2 | 6 |
| D3 | 7 |
| RST | not wired (software reset) |

Touch / sensors I2C: **SDA 15**, **SCL 14**.

SPI host: typically **SPI2_HOST**. RGB565, QSPI mode.

## Host / silico

| Item | Fact |
|------|------|
| USB-Serial/JTAG | Preferred serial on Windows often **COM** with vid `303a` pid `1001` |
| Identity (C plate) | App must answer host word `identity` with `fw_name=… fw_version=…` on the link |
| Deploy | `silico deploy --port COMx --yes` → `idf.py -C firmware -p COMx flash` |
| PSRAM | Enable **SPIRAM OCT 80 MHz** + `SPIRAM_USE_MALLOC` for full-frame RGB565 buffers (~330 KB × N) |
| Flash size | Configure **16 MB** in sdkconfig (defaults matter; old 2 MB images mislead tools) |

## Framebuffers

Full native RGB565 frame is **368 × 448 × 2 ≈ 330 KB**. Dual logical+panel buffers ≈ **660 KB** — **PSRAM required** or first boot `abort()`s on `heap_caps_malloc` failure.

Pattern that worked:

1. Draw **product face** in **logical landscape** (e.g. 448×368).  
2. Blit with **90° rotation** into panel buffer.  
3. Push panel buffer in **horizontal stripes** (height even; 16 px is fine).  
4. Byte-swap RGB565 for QSPI the same way Waveshare colorbar does (`SPI_SWAP_DATA_TX` / hi-lo swap).

### Rotation (operator-confirmed upright map)

Canonical board intent: USB + banner chrome on the **top** edge of the landscape **product face**.

| Direction | Panel ← logical (forward) | Logical ← panel (inverse, for present loops) |
|-----------|---------------------------|-----------------------------------------------|
| **CCW 90° (default upright for this board class)** | `px = FACE_H - 1 - ly`, `py = lx` | `lx = py`, `ly = FACE_H - 1 - px` |
| CW 90° (wrong on first metal — **product face** upside-down) | `px = ly`, `py = FACE_W - 1 - lx` | `lx = FACE_W - 1 - py`, `ly = px` |

**Field lesson (LVGL product face, 2026-07):** first metal + first LVGL pass both shipped **CW** and the operator reported **upside-down**. Switching present() to **CCW** fixed it. Agents: default to **CCW** on this board class; if the **product face** is upside-down, flip CW↔CCW in the present path only — do **not** re-layout product UI.

Document any counter-example (unit that needs CW) here with date + board revision, do not leave it only in chat.

### Rounded corners (chrome inset)

The physical AMOLED has **rounded corners**. Banner labels flush to x=0 / x=W−1 **clip** (e.g. only the last stem of a wide glyph visible).

**Rule:** inset left/right banner text by roughly **one large glyph** (~24–32 device px at 448-wide **product face**). Do **not** move labels down to fix clipping — only horizontal inset.

## First-boot black after flash

Observed: after `idf.py` / `silico deploy` USB-JTAG reset, panel stays **black/noop** until **unplug/replug** power.

Mitigations that help in firmware:

1. Short settle (**~80 ms**) between `panel_reset` and `panel_init`.  
2. Sleep-out delay in init table (**~100 ms** on 0x11) as in Waveshare colorbar.  
3. `disp_on_off(true)` then another short delay + **second** `disp_on_off(true)`.  
4. Host: if inspect only sees identity but operator reports a black **product face**, ask for a **power cycle**, then re-check — do not thrash full-erase redeploys for “blank” alone when identity is healthy.

If identity fails and serial shows `abort()` at framebuffer alloc: **PSRAM not enabled** in sdkconfig (defaults not applied until clean reconfigure).

## BOOT / user button (GPIO0)

Module **BOOT** is often **GPIO0** (active low, internal pull-up). Treat it as a generic user button on this board class when product hard keys are not yet wired. **Map product meaning in the GCU** — do not hard-code vertical control labels in board knowledge.

## Init sequence reference

| Revision | Where to copy from |
|----------|--------------------|
| **V2 / CO5300** | Waveshare `examples/esp-idf/13_display_colorbar` (command table with `0xFE/0xC4/0x3A/…/0x11` sleep out / `0x29` display on, brightness `0x51=0xFF`) |
| **Original / SH8601** | Waveshare SH8601 example / `esp_lcd_sh8601` init for that revision — not the CO5300 colorbar table |

Keep the chosen table in the GCU, not reinvented from memory.

## What “good” looks like on metal

- Panel shows a non-black **product face** after power-on (or after power cycle if first post-flash boot was dark).  
- Landscape **product face** paints correctly (logical 448×368 present, upright with USB on the top edge).  
- Banner chrome fully legible (inset past rounded corners).  
- `silico inspect --port COMx` → `fw_name` / `fw_version` match host.

Product-specific dials, units, and key semantics belong in the **GCU**, not here.

## Anti-patterns

- Applying **one** init path to both revisions: original/FT3168 needs **SH8601**; V2/CST816 needs **CO5300**. Listing text alone is not a probe.  
- On V2 units, falling back to SH8601 after a black panel and calling that “done” without trying the CO5300 colorbar path.  
- On original units, forcing the V2 CO5300 sequence and black-screening a panel that would work on SH8601.  
- Full internal-RAM double framebuffer without PSRAM.  
- Flushing full-panel transfers larger than SPI `max_transfer_sz` without striping.  
- Banner text at x=0 on rounded AMOLED.  
- Treating post-flash black + healthy identity as “flash failed” and erasing again without a power cycle.  
- Embedding one GCU’s vertical controls or acceptance UI in this board topic.

## See also

- [esp32-lcd-ips.md](esp32-lcd-ips.md) — SPI IPS (different class)  
- [esp32-usb-serial.md](esp32-usb-serial.md) — duplex / console  
- [first-flash.md](first-flash.md) — esptool path  
- Upstream: [waveshareteam/ESP32-S3-Touch-AMOLED-1.8](https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-1.8)
