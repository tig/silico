# esprec — agent eyes on ESP displays (**ready**)

**Status:** **implemented** as external tooling ([tig/esprec](https://github.com/tig/esprec)).
Not a silico package feature. Open this file only when the GCU has a **screened
ESP32-class** product face and you need capture — not for LED-only or audio-only
first ship.

esprec is the [tuirec](https://github.com/tui-cs/tuirec) *analogue* for **device
screens** (mission kinship, not a port of tuirec’s PTY/cast pipeline): on
command, on-device capture → USB serial → host **PNG** (snapshot) or **GIF**
(keyframe or continuous sequence).

## Relationship to silico (do not soft-fork)

| Silico concept | Role | esprec role |
|----------------|------|-------------|
| **product face** | Operator **see/hear** acceptance for first ship | Optional **agent** evidence of the screen face — does **not** replace operator confirm on first ship |
| **sim** / host plant | GCU `sim/` HAL double + pytest/CTest | **Not** esprec. Do not rename GCU sim to “QEMU” |
| **host gate** | Named product gate (`pytest` / `silico gate`) | GCU CI stays this; do **not** force every GCU to run QEMU |
| **QEMU gate** | — | esprec’s own CI ladder (unit required; QEMU example may be follow-up). Proves esprec’s capture path, not every GCU plant |
| **metal** | Real USB + operator-observable face | Real panel still confirms color/timing quirks |

**Apps stay apps.** Product domain UI stays in the GCU. esprec is **tooling**
(firmware component + host CLI). Prefer sibling clone + `pip install -e` until
a second GCU forces a silico pin (**Extract, then open**).

## Readiness (current)

| Bar | State |
|-----|--------|
| Host CLI (`esprec snapshot` / `record` / `agent-guide`) | **yes** |
| On-device component (`component/esprec`, `esprec_emit_rgb565_spi_be`) | **yes** |
| Unit gate `python -m pytest -q` (protocol integrity, PNG/GIF, fake device) | **yes** |
| QEMU CI example | **follow-up** if env lacks it — metal + unit are honest for firmware path |
| Agent guide | `esprec agent-guide` |

## Install / invoke

```text
# sibling layout (typical): …/tig/esprec next to …/tig/<gcu>
python -m pip install -e "../esprec[dev]"
esprec agent-guide
esprec snapshot --fake -o face.png          # offline
esprec snapshot --port COMx -o face.png     # metal still
esprec record --port COMx --frames 5 --hz 2 -o clip.gif
# named unit gate:
python -m pytest -q   # inside the esprec checkout
```

Device commands: `esprec shot` or `shot` (alias). Wire: **ESPREC1** header +
base64 raster + end line; CRC covers **metadata + raster** (fail closed on
truncate / header tamper). Legacy `SHOT` (pixels-only CRC) still decodes.

**Serial open:** esprec sets DTR/RTS low before open so ESP auto-reset does not
reboot mid-session (black unpainted shadow). Prefer **one open session** for
btn inject + multiple snaps (see esprec `scripts/xuss_c_screen_scenario.py`).

## Agent recipe

**Where we are:** Stage D (hello metal) or UI domain work after deploy. Host
gate is green; board talks; product face includes a **screen**.

**Why:** Agents cannot trust “UI looks right in source.” A PNG/GIF of the live
buffer is evidence; the operator still owns first-ship product face judgment.

```text
# After confirmed deploy + app running (soft-reset if verify parked the loop):
esprec snapshot --port COMx --command shot -o .silico/esprec/face.png
# Read the PNG (vision) vs product face “good.”
# Multi-step: keep one serial session; settle after each product action; then snap.
```

Rules:

1. **Announce** before capture if UI will change brightness/content surprisingly.
2. Prefer **snapshot** for “what is on screen now?” Prefer **bounded GIF** for
   sequences — never unbounded streams.
3. Store under **gitignored** paths (e.g. `.silico/esprec/`) unless product docs want stills.
4. **Do not** claim metal acceptance from PNG alone on first ship — still ask the operator.
5. **Do not** add esprec QEMU jobs to every GCU `ci.yml` by default.
6. If PNG disagrees with the glass: **pipeline first** (integrity, packing, cooked serial), not product folklore.

## Integration surface (GCU)

1. EXTRA_COMPONENT_DIRS → `esprec/component` (sibling clone) or vendor `component/esprec`.
2. Maintain a full-frame **shadow** RGB565 (`spi_be` packing as on panel DMA).
3. On `shot` / `esprec shot`: hush logs, call `esprec_emit_rgb565_spi_be(shadow, w, h)`.
4. Document host one-liner in product `install/` when capture is part of the update path.
5. Panel color/partial paint: [esp32-lcd-ips.md](esp32-lcd-ips.md) when relevant.

## What not to do

- Treat esprec as silico’s default **sim** (HAL plant).
- Require QEMU on cloud CI for every GCU.
- Claim first ship complete from agent-viewed PNG without operator product face confirm.
- Embed product UI logic into silico or esprec.
- Reopen serial with default DTR/RTS between every snap (resets ESP, black frames).

## Compound

Protocol/CRC/serial friction → fix **tig/esprec**. Board-generic panel notes →
this knowledge tree. Product domain → GCU.
