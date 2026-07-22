# ESP32 IPS LCD color and partial paint (self-improving)

Host notes for GCUs that drive a small **SPI IPS panel** from classic ESP32 under MicroPython (ILI9341 / **ILI9342** class, M5-class cores). Not product face art.

When you learn a new host truth on a bench, **add a bullet here**.

## Do not trust “standard RGB565” by folklore

On several M5-class boards (M5GO / Core with ILI9342-class panels):

1. **Display inversion** may be required (`INVON` / command `0x21`) so black is black and hues are not inverted.
2. **R and B in the RGB565 word may need swapping** relative to textbook RGB565 so **on-panel color matches SK6812 / NeoPixel side LEDs** driven with the same logical RGB triple.
3. SPI byte order for each pixel is typically **big-endian** 565 (hi byte then lo byte) in a bulk blit buffer — confirm with a solid red/green fill, not only with “it looks colorful.”

### Measure recipe (operator map)

1. Paint side LEDs pure **red (255,0,0)**, **green (0,255,0)**, **blue (0,0,255)**.
2. Paint the same logical RGB on the LCD fill.
3. If LEDs and panel disagree, try R↔B in the 565 pack **before** rewriting product themes.
4. Record the working pack in the GCU HAL; promote the durable rule **here** if it is board-class generic.

Example pack that matched one M5GO IPS bench map (panel presents BGR-ish 565):

```text
# logical r,g,b → 565 with R/B swapped into the word
word = ((b & 0xF8) << 8) | ((g & 0xFC) << 3) | (r >> 3)
```

Do **not** copy this blindly to every ILI9341 module; **measure**. Document the measured map in the GCU.

## MADCTL / INVON

- Wrong MADCTL BGR bit and missing INVON produce “wrong theme” bugs that look like product palette errors.
- Fix **panel path** first; only then tune theme RGB tables.
- Pure primaries on LEDs (`(255,0,0)` not `(255,48,48)`) make mismatches obvious.

## Partial updates (SPI thrash)

Full-panel `fill` every animation tick:

- costs large SPI time,
- can couple noise into a speaker amp on the same board,
- flashes chrome the user expects to stay put.

Prefer:

| Change | Paint |
|--------|--------|
| Scrolling status / “hair” bar | Compose strip in RAM → one `blit` of that rectangle |
| Single eye wink | Clear/redraw **that eye’s rect** only |
| Sensor value field | Compose fixed-width text strip → blit; do not refill labels |
| Theme / mode change | Full clear is OK |

Off-screen compose (bytearray of RGB565) + windowed SPI write is the durable pattern.

## Agent checklist

1. Open this file when the product has an SPI IPS face or status UI.
2. Ground colors with **LED vs panel** measurement, not host-monitor screenshots alone.
3. Prefer regional blit for continuous animation.
4. Extend this file when a new panel family needs a different pack or init sequence.
