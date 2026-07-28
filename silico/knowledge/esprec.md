# esprec — agent eyes on ESP displays (when ready)

**Status:** companion tooling is **not** shipped as a silico package feature.
Upstream: [tig/esprec](https://github.com/tig/esprec) (requirements / CI shape;
implementation landing later). Open this file only when the GCU has a **screened
ESP32-class** product face and you need capture, not for LED-only or audio-only
first ship.

esprec is the [tuirec](https://github.com/tui-cs/tuirec) equivalent for **device
screens**: on command, on-device capture → USB serial → host **PNG** (snapshot)
or **GIF** (short record) so agents can **see** the panel without a camera.

## Relationship to silico (do not soft-fork)

| Silico concept | Role | esprec role |
|----------------|------|-------------|
| **product face** | Operator **see/hear** acceptance for first ship | Optional **agent** evidence of the screen face — does **not** replace operator confirm on first ship |
| **sim** / host plant | GCU `sim/` HAL double + pytest/CTest | **Not** esprec. Do not rename GCU sim to “QEMU” |
| **host gate** | Named product gate (`pytest` / `silico gate`) | GCU CI stays this; do **not** force every GCU to run QEMU |
| **QEMU gate** | — | Lives in **esprec’s** CI ([specs/ci.md](https://github.com/tig/esprec/blob/main/specs/ci.md) via [tobozo/esp32-qemu-sim](https://github.com/tobozo/esp32-qemu-sim)): unit → QEMU → optional metal. Proves esprec’s capture path, not every GCU plant |
| **metal** | Real USB + operator-observable face | Real panel still confirms color/timing quirks QEMU cannot prove |

**Apps stay apps.** Product domain UI stays in the GCU. esprec is **tooling**
(firmware component + host CLI). Pin or vendor only when a GCU needs it —
prefer treating it as an external tool until a second GCU forces a silico pin
(**Extract, then open**).

## When ready (readiness bar)

Treat esprec as **usable by agents** only when **all** of these are true:

1. Upstream ships a host CLI (or library) agents can run non-interactively with
   stable flags and exit codes.
2. On-device component has a documented integration surface (raw framebuffer
   and/or LVGL snapshot path).
3. Upstream **unit** gate is green without metal.
4. Upstream **QEMU** gate is green (example firmware + capture assertion), or
   metal capture is proven and documented if QEMU is temporarily unavailable.
5. `esprec --help` / agent-guide (or equivalent) exists so agents do not read
   source to discover the capture command.

Until then: **do not** invent a parallel capture stack in silico or the GCU
“because esprec is coming.” Use operator observe + product docs. File friction
on [tig/esprec](https://github.com/tig/esprec) if the gap blocks UI work.

## Agent recipe (after ready)

**Where we are:** Stage D (hello metal) or UI domain work after deploy. Host
gate is green; board talks; product face includes a **screen**.

**Why:** Agents cannot trust “UI looks right in source.” A PNG/GIF of the live
buffer is evidence; the operator still owns first-ship product face judgment.

```text
# After confirmed deploy + app running (soft-reset if verify parked the loop):
# 1. Confirm esprec is installed / on PATH (or GCU-documented path).
# 2. Snapshot (illustrative — use real flags from esprec help when shipped):
esprec snapshot --port COMx --out .silico/esprec/face.png
# 3. Read the PNG (vision / multimodal) and compare to product face “good.”
# 4. For multi-step UI checks, bounded record → GIF (finite frames/duration).
```

Rules:

1. **Announce** before capture if the product UI will change brightness/content
   in a surprising way (same spirit as surprising metal effects).
2. Prefer **snapshot** for “what is on screen now?” Prefer **bounded GIF** for
   boot/navigation sequences — never unbounded stream that can fill disk.
3. Store captures under **gitignored** paths (e.g. `.silico/esprec/`) unless the
   product explicitly wants checked-in docs stills.
4. **Do not** claim metal acceptance from PNG alone on first ship — still ask
   the operator whether the documented product face is true on the bench.
5. **Do not** add esprec QEMU jobs to every GCU `ci.yml` by default. Rely on
   esprec’s own CI for component honesty; GCU may optionally add a snapshot
   step later when the product needs regression visuals.

## Integration surface (GCU)

When adopting esprec in a screened GCU:

1. Link the component per esprec’s firmware-api (when published); keep capture
   polite (bounded RAM; product UI continues after capture).
2. Coexist with product serial logging — structured capture must be recoverable
   amid log noise.
3. Choose **raw framebuffer** vs **LVGL snapshot** explicitly in product docs /
   HAL; do not silently guess.
4. Host path: document the one-liner in product `install/` or `scripts/` only
   after the tool is ready (same commands as CI when the GCU opts into capture).
5. Panel path still needs color/partial-paint host knowledge when relevant:
   [esp32-lcd-ips.md](esp32-lcd-ips.md) (and any other **in-tree** panel topics under
   `silico/knowledge/` for the board class — do not link unmerged topic files).

## What not to do

- Treat esprec as silico’s default **sim** (HAL plant) or replace `sim/hal_double`.
- Require QEMU on cloud CI for every MicroPython or LED-only GCU.
- Claim first ship complete from agent-viewed PNG while the operator never
  confirmed product face.
- Embed product UI logic into silico or into esprec.
- Build a private camera-on-desk folklore path when esprec is ready and the GCU
  already embeds the component.

## Compound

If the path is rough (serial framing, QEMU serial attach, LVGL major drift):
prefer a durable fix or issue on **tig/esprec**; promote a silico knowledge note
here only when the truth is host/board-generic beyond the tool itself.

## Spec map (upstream)

| Spec | Scope |
|------|--------|
| [esprec specs/spec.md](https://github.com/tig/esprec/blob/main/specs/spec.md) | Product requirements |
| [esprec specs/ci.md](https://github.com/tig/esprec/blob/main/specs/ci.md) | Unit → QEMU → optional metal |
