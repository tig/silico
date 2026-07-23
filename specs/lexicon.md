# Silico lexicon

Short definitions for phrases that carry load in silico docs. Prefer this file when an agent or human is stuck on jargon. For rules of behavior, see [tenets.md](./tenets.md). For the build target, see [silicov1.md](./silicov1.md). For the Fall 2026 ambition, see [wb-2026-fall-three-gcus.md](./wb-2026-fall-three-gcus.md).

Jump: [Core](#core-product-words) ┬╖ [Done & gates](#done-gates-and-honesty) ┬╖ [Agents](#prompt-agents-operators) ┬╖ [Dependency & architecture](#dependency-and-architecture)

---

## Core product words

### silico

The open [**spine**](#spine) at [github.com/tig/silico](https://github.com/tig/silico): host library, [plate](#plate), agent contracts, doctrine, and CI for those pieces. Not a company SKU. Not a [GCU](#gcu). Not the vertical domain app. Device `firmware/` never imports silico; only Mac/CI [host](#host) paths do.

See also: [pin](#pin), [plate](#plate).

### GCU

**General Contact Unit.** One **shippable edge product**: app + [metal](#metal) with end-user value, private domain logic, and a life after the bench. [Silico](#silico) is the [spine](#spine) GCUs [pin](#pin) on the [host](#host). Each GCU is priced and branded as a product; silico is free (Apache-2.0). Public silico docs name starter GCUs only by codenames (see [gcu-codenames.md](./gcu-codenames.md)).

See also: [GCV](#gcv), [plate](#plate).

### GCV

Placeholder for a future product class if we need a name beyond [GCU](#gcu). Not defined in v1. Do not invent GCV features in public docs until a real need forces the word.

### spine

Shared [host](#host) infrastructure and contracts that more than one [GCU](#gcu) can [pin](#pin): deploy/verify, [host gate](#host-gate), [plate](#plate) layout, agent docs, non-secret examples. The spine is **not** the product. [Promoting](#promote) private domain into the spine to win a demo is a failure (Apps stay apps).

See also: [silico](#silico), [gobbledygook](#gobbledygook).

### plate

The **template** [GCU](#gcu) repo layout and conventions (folders, `AGENTS.md`, `silico.toml`, host [pin](#pin), CI that runs the [host gate](#host-gate)). Scaffolding a GCU means following the plate, not inventing a parallel tree. Default: MicroPython `gcu`. Opt-in: C/ESP-IDF `gcu-c` (`silico scaffold . --plate gcu-c`). Default plate is a product choice, not a quality ranking (see [tenets](./tenets.md)).

See also: [spine](#spine), [scaffold](#scaffold).

### scaffold

Also **scaffolding.** The host verb (`silico scaffold`) and the act of **laying down the [plate](#plate)** into a product checkout: standard folders, `silico.toml`, host [pin](#pin), HAL/sim stubs, and CI hooks. Scaffold merges into an existing [GCU](#gcu) without overwriting product `README.md` / `spec.md`. It is not writing domain firmware and not inventing a parallel repo layout.

See also: [plate](#plate), [pin](#pin).

### metal

The physical board (and the behavior that only appears on real hardware). **Metal confirms**; it does not define **done**. Opposite of host-only proof.

See also: [host-first](#host-first), [host gate](#host-gate), [Prompt to metal](#prompt-to-metal), [sim](#sim).

### host

The developer or CI machine (Mac, Windows, Linux runner): Python, pytest, [sim](#sim), deploy tools, version parse. [Silico](#silico) as a package lives **on the host only**.

See also: [host path](#host-path), [host-first](#host-first).

### host path

Everything agents and humans run on the [host](#host) to set up, prove, deploy, and verify: install tools, [pin](#pin) packages, CI, port discovery, flash/update, [version verify](#version-identity). Tenet: Agents operate the host path.

See also: [gobbledygook](#gobbledygook), [Help the operator](#help-the-operator).

### product face

The **human-observable product indication** on the [GCU](#gcu) after the app is running: what the [operator](#operator) is supposed to **see or hear** without reading a serial terminal (status LEDs, light pattern, boot riff / speaker, screen cue, etc.). Documented in product `spec.md` / `install/` “good.”

**Not** the same as: deploy verify success, `FW_VERSION` over REPL, or a generic [plate](#plate) hello on a module GPIO that is not the product’s intended signal.

Always say the full term **product face**. Never shorten to bare “face.” On first use in a session, define it (see silico `AGENTS.md` operator language). First-ship [metal](#metal) acceptance requires the operator to confirm the product face, not only a version string.

See also: [metal](#metal), [host gate](#host-gate), [Help the operator](#help-the-operator), [first ship](#first-ship).

### first ship

Also **first-ship path.** The ordered getting-started path from cold start to an operator-observable [product face](#product-face) on [metal](#metal): tools → workspace → [plate](#plate) + [host gate](#host-gate) → board talk + confirmed deploy + see/hear. **Not** a calendar day and not “we’ll finish tomorrow.” Say **first ship**, never “Day 1.”

Chunks of the path are [**stages**](#stage) (Stage 0 welcome, A tools, B workspace, C plate, D metal, …). After first ship: the **update path** (how you change and re-flash next time), not “Day 2.”

See also: [stage](#stage), [Help the operator](#help-the-operator), [Prompt to metal](#prompt-to-metal).

### stage

One **short ordered chunk** of the [first ship](#first-ship) path (Stage 0, A, B, C, D, E, F). Prefer **stage** over **phase** (phase sounds long and waterfall). When saying “where we are,” use stage letter + plain name from the first-ship map in root `AGENTS.md`.

See also: [first ship](#first-ship), [gate](#gate).

---

## Done, gates, and honesty

### gate

A **named checkpoint** that must pass before the agent claims progress or advances. In silico talk this usually means either:

1. **[Host gate](#host-gate)** — automated proof on the [host](#host) (pytest / `silico gate` / product-path). Green means the change is claimable as host-done.
2. **Operator gate** — a structured yes/no or physical confirm (`bedside ask` / `bedside step`, or the agent host's picker) before a scary or irreversible act (board identity, deploy overwrite, plug cable).

Do not say "the gate" to an operator without saying *which* gate and what green/pass means in plain language. On first use in a session, define the term (see silico `AGENTS.md` operator language).

See also: [host gate](#host-gate), [Help the operator](#help-the-operator).

### host-first

Doctrine: **done lives on the [host](#host)** (named tests, compile gates, [sim](#sim)/scenario gates) before anyone treats a device flash as proof. [Metal](#metal) confirms after the [host gate](#host-gate) is green. Enables a non-expert to trust agent work without lying.

See also: [host-honest](#host-honest), [test-first](#test-first), [Prompt to metal](#prompt-to-metal).

### test-first

Write (or update) automated tests and the [host gate](#host-gate) expectations **before** or alongside the product change - not after a flash-and-see loop. Agents author detailed specs, unit/smoke tests, and `firmware/` under test-first and [host-first](#host-first) together. Red tests that later go green are the proof trail; "I ran it on the board" is not.

See also: [sim](#sim).

### host-honest

Also **host-honest done.** Colloquial for the same bar as [host-first](#host-first) when we stress *truth*: a green [host gate](#host-gate) that actually means something about the firmware, not theater. "Host-honest done" = claim done only when the named host command is green under that contract.

### host gate

The **named** [host](#host) command (or CI job) that must be green for a change to count as done. Typically pytest (and related compile/[sim](#sim) checks) on the [GCU](#gcu) repo. Red means not done. "I flashed it on my desk" is not a gate. CI has no serial port; hardware harness is optional and local.

See also: [host-first](#host-first).

### version identity

Also **version verify.** Install and update fail closed unless device-reported `FW_VERSION` (and related identity) matches what the [host](#host) deployed. Mismatch is failure, not a warning.

See also: [integrity](#integrity), [Prompt to metal](#prompt-to-metal), [gobbledygook](#gobbledygook).

### integrity

Also **update integrity.** Hardening so field updates are trustworthy beyond version string match (hash manifest, signing, provenance, CRA-related hooks, etc.). Definition open - see the integrity spike. **Not** a first-ship or early update-path requirement; belongs on the month-later beta horizon.

See also: [version identity](#version-identity).

### sim

Also **host plant** / **closed-loop plant.** [Host](#host)-only simulation of the product world used for regression without a board. Never deployed to the device. Complements [metal](#metal); does not replace [host gate](#host-gate) or real USB on first ship.

See also: [HAL](#hal), [host-first](#host-first).

---

## Prompt, agents, operators

### Prompt to metal

Tagline and tenet: use agent prompts so what the team **cares about** lands on edge devices reliably, safely, and repeatedly. The experience we work backwards from: agent on a Mac, device end-to-end the next day, potential customer's hand the day after, [silico](#silico) still foundational. [Host gates](#host-gate), [version verify](#version-identity), and agent docs are the product surface for that prompt - not folklore.

See also: [host-first](#host-first), [metal](#metal).

### Help the operator

Also **bedside manners.** Assume low ops literacy; do the work when you can; one step at a time for physical/browser steps; never dump a wall of unexplained shell. Violating this violates Agents operate the host path.

In **silico**, agent docs add domain operator language on top of Bedside (not a fork of the nine principles): (1) the **first prompt** reminds what Silico is and summarizes **this** [GCU](#gcu); (2) silico terms ([GCU](#gcu), [host](#host), [plate](#plate), [scaffold](#scaffold), [first ship](#first-ship), [stage](#stage), [gate](#gate), [host gate](#host-gate), [metal](#metal), [product face](#product-face), [pin](#pin), …) are **defined on first use** and spoken as their **canonical lexicon names** (no invented short forms such as bare “face” for product face); (3) big human steps include **why** and **where** on the first-ship map. Canonical rules: silico root `AGENTS.md` → Operator language.

See also: [operator](#operator), [Grady](#grady).

### operator

The human in the loop - often [**Grady-shaped**](#grady) (domain or hardware judgment, not a career embedded/DevOps engineer). Owns judgment and confirmation, not typing C/MicroPython into a blank file or memorizing serial folklore.

See also: [Help the operator](#help-the-operator).

### Grady

Also **Grady-shaped.** Persona for the non-software (or non-embedded) founder/builder who should complete [first ship](#first-ship) and the update path with an agent, without staffing a device-ops cult. Used as the customer shape for [**Prompt to metal**](#prompt-to-metal), not as a public product brand.

See also: [operator](#operator).

### gobbledygook

The hard boring edge ops that vertical teams should not re-learn: port discovery, multi-COM hazards, deploy file sets, [version verify](#version-identity), recovery, anti-patterns, CI that means something about [metal](#metal). [Silico](#silico) invests here so [GCUs](#gcu) do not each invent it.

See also: [host path](#host-path), [spine](#spine).

---

## Dependency and architecture

### pin

Also **package pin.** [GCU](#gcu) `requirements-dev.txt` (or equivalent) depends on [silico](#silico) by **tag or SHA** (or editable path while extracting). Pin is necessary for first-ship foundation; not sufficient without CI [host gate](#host-gate) and real [metal](#metal) path.

See also: [plate](#plate).

### promote

Also **promote to silico.** Move a pattern from a private [GCU](#gcu) into the public [spine](#spine) when a second GCU needs it. Do not promote to win demos or to dump domain logic.

See also: [spine](#spine).

### Pi-class

MCU class for many v1 starters: **RP2040-class** boards, typically MicroPython, UF2 first-flash, then USB serial file deploy. Still a common default path; not the only supported class (see **ESP32-class**).

See also: [plate](#plate), [ESP32-class](#esp32-class).

### ESP32-class

MCU class on the silico spine: classic ESP32 and S3-class boards. Supported runtimes: **MicroPython** (esptool first-flash, then mpremote) and **C / ESP-IDF** (`gcu-c` plate; image flash). Not the same as Arduino-core ESP boards as a silico backend.

See also: [Pi-class](#pi-class), [plate](#plate).

See also: [silicov1.md](./silicov1.md), [metal](#metal).

### HAL

**Hardware abstraction layer.** Device firmware contract: I/O and time as boring values (ints, floats, bools), not driver objects at the boundary. Host [sim](#sim) implements the same shape. No hardware at import time; `init` constructs the world.

See also: [host-first](#host-first), [sim](#sim).

### agent-first CLI

CLI designed so agents can drive it with thin, scriptable verbs and clear exit codes (e.g. doctor, gate, deploy --verify), not only interactive human TUI. Related design discussion may live outside this repo (e.g. tui-cs/cli issues).

See also: [host gate](#host-gate), [Help the operator](#help-the-operator).
