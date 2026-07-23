![Silico - Prompt to metal](docs/hero.jpg)

Silico makes building maintainable firmware for embedded devices simple. Given a device [spec](./specs/lexicon.md#spec), it first guides AI agents to [scaffold](./specs/lexicon.md#scaffold) a GitHub repository set up for long-term maintainability.

Agents then loop to engineer robust firmware, unit and smoke tests, a simulator, continuous integration (CI) using both real devices and the simulator, and an end-user install/upgrade tool.

The human interface is a coding agent, not an installation guide or shell tutorial.

> ***[Prompt to metal (n)](https://blog.kindel.com/2026/07/22/prompt-to-metal/)***: *Building hardware products from expressed human intent. The high-judgement engineer and/or product person describes and judges; the machines draw the schematics, route the boards, write the firmware and companion software, run the tests, manage customer feedback, and improve the product.*

## Silico works backwards from this

> *With just Claude Code on my Mac and my hardware spec, I had the device working end-to-end in a few hours, and in a field test the day after that. Silico is now a foundational piece of our company's technology.*

Agents write the firmware. The human owns the judgment.

## Definitions

Silico uses a highly opinionated lexicon to keep AIs and humans on the same page. See [Lexicon](./specs/lexicon.md) for the full dictionary; these terms matter for getting started:

### GCU

**General Contact Unit.** One **shippable edge product** with end-user value, private domain logic, and an install/upgrade system.

### Host

**The developer or CI machine** (Mac, Windows, Linux runner). The Silico simulator, OSS embedded tooling, test infrastructure, and deploy tools all run on the host; not on the board.

### Spine

The shared **host tooling and contracts** Silico provides (deploy, host gate, plate, agent docs). More than one [GCU](./specs/lexicon.md#gcu) can [pin](./specs/lexicon.md#pin) it. The spine is not the product; each GCU is.

### Plate

The **template** [GCU](./specs/lexicon.md#gcu) repo layout and conventions (folders, `AGENTS.md`, `silico.toml`, CI workflows). Scaffolding a GCU means following the plate. The default is MicroPython.

### Scaffold

The act of **laying down the [plate](./specs/lexicon.md#plate)** into a product checkout: `./AGENTS.md`, standard folders, `silico.toml`, host [pin](./specs/lexicon.md#pin), [HAL](./specs/lexicon.md#hal)/sim stubs, and CI hooks.

## Getting Started

### Step 0: Prerequisites

1. **Engineer the device** (or use a known board kit). Custom hardware, a prototype, or a starter kit like the M5GO in the examples below. Use a USB data cable so the host can talk to the board. Silico covers firmware and the host path on that board, not PCB design.
2. **Know roughly what the product must do.** Let the agent help refine the [spec](./specs/lexicon.md#spec). Do not expect the agent to invent the product.
3. **A Mac or PC, a GitHub account, and a coding agent** (TUI or GUI).

### Step 1: The Spec

Put the specification for the device (hardware and end-user functionality) in a GitHub repo. These example repos each contain a [spec](./specs/lexicon.md#spec) that has been proven to work with Silico:

- [Xuss](https://github.com/tig/xuss) - A demo device based on the [M5Stack M5GO IoT Starter Kit v2.7](https://shop.m5stack.com/products/m5go-iot-starter-kit-v2-7), using [MicroPython](https://github.com/micropython). Intentionally specifies a simple implementation using Python to illustrate that path.
- [Xuss-C](https://github.com/tig/xuss-c) - A demo device based on the [M5Stack M5GO IoT Starter Kit v2.7](https://shop.m5stack.com/products/m5go-iot-starter-kit-v2-7), using C and native ESP32 development. Intentionally specifies a more sophisticated implementation with higher performance and usability to illustrate that path.
- [Xuss-Lame](https://github.com/tig/xuss-lame) - A demo device based on the [M5Stack M5GO IoT Starter Kit v2.7](https://shop.m5stack.com/products/m5go-iot-starter-kit-v2-7) that is intentionally under-specified. This demonstrates Silico's ability to interview the human to refine the spec and requirements interactively.

### Step 2: Start the AI Agent

#### If using an Agent TUI (`claude`, `grok`, `copilot`, …):

Start the session from within a local checkout of the [GCU repo](./specs/lexicon.md#repo):

```sh
git clone https://github.com/tig/xuss
cd xuss
grok
```

In the above example, `tig/xuss` is the repo for one of the Silico example GCUs; replace it with the repo containing the real GCU.

#### If using an Agent GUI (Cursor, Claude Code, GitHub Copilot App, …):

* Start a new project using the Agent GUI's method for doing so.
* Point the project at the GitHub repo with the spec in it.

### Step 3: Tell the agent to create the [first ship](./specs/lexicon.md#first-ship)

Give the agent this starting prompt:

```md
See https://github.com/tig/silico. Follow the getting started instructions for agents.
```

 The agent will ask questions, suggest options, and otherwise guide the process through [first ship](./specs/lexicon.md#first-ship); it will use Silico [bedside manners](https://github.com/tig/bedside), install or upgrade [host](./specs/lexicon.md#host) tooling (with consent), including the GitHub CLI (`gh`).

When [first ship](./specs/lexicon.md#first-ship) is complete, the agent will land the following on the default branch (e.g. `main`), following the repo's contribution standards:

* `./AGENTS.md` - Self-improving Silico agent guidance.
* `./firmware` - Device firmware that implements the spec and is proven on real metal.
* `./sim` - Bespoke [HAL](./specs/lexicon.md#hal) and [simulator](./specs/lexicon.md#sim) for host and CI verification.
* `./install` - Install and upgrade tool for end users to put firmware on the GCU.
* `.github/workflows/ci.yml` - GitHub workflow on `push` and `pull_request` that tests and validates the firmware.
* Other files and folders required for the GCU to implement the GCU spec.

### Steps 4-n: Iterate and Improve

Use AI agents to refine the GCU. E.g.:

```
Create a new PR to lower the volume of the bootup sound by 10%.
```

On each push to `main` or PR merge, CI will run with validation and regression testing on the bespoke simulator Silico helps create.

At the start of each new agent session in the repo, follow agents will follow `./AGENTS.md` so work continues to use Silico on the GCU.

## Real World Examples

Silico was built and improved while engineering the firmware and software for these real-world [GCUs](./specs/lexicon.md#gcu).

* **Zakalwe** - A closed-loop control module that upgrades classic BMW, Volvo, and Mercedes cars from the '80s, by [Holy Grail Labs](https://www.holygraillabs.com). This device has no internet connectivity and replicates a 1970s-era control device containing more than 100 discrete logic parts. RP2040-class board; firmware is MicroPython.
* **Quilan** - A solar-powered field logger with environmental and atmospheric sensors and LoRaWAN cloud connectivity. ESP32-class board; firmware is C.
* **Sma** - A tiny, battery-powered, sleep-friendly remote sensing and mesh-connected device. RP2040-class board; firmware is MicroPython.

Submit PRs to add more real-world GCU examples above.

## Supported platforms (host spine)

| MCU class | Device runtime | First flash | App update | [Plate](./specs/lexicon.md#plate) |
|-----------|----------------|-------------|------------|--------|
| **RP2040-class** | MicroPython | UF2 (once) | `mpremote` file copy | `silico scaffold .` (default `gcu`) |
| **ESP32-class** | MicroPython | esptool (once) | `mpremote` file copy | default `gcu` + ESP board pin |
| **ESP32-class** | **C / ESP-IDF** | esptool / `idf.py flash` | same image path | `silico scaffold . --plate gcu-c` |

Default for new GCUs is **MicroPython**. **C** on ESP-IDF is opt-in when a product needs native firmware against the same host path.

### Not Silico runtime paths (yet)

These may appear *inside* a GCU's own tree; they are **not** first-class Silico [plates](./specs/lexicon.md#plate) or `[runtime].language` values, yet:

- **Arduino** core / `arduino-cli` as the first ship deploy backend ([issue #59](https://github.com/tig/silico/issues/59)).
- **PlatformIO** as the Silico deploy path.
- **Pico SDK (C)** as a Silico language peer (only if an RP2040 GCU forces it later).
- **`language = cpp`** as a third peer next to MicroPython and C (C++ may live in ESP-IDF board TUs; host-gated domain stays portable C by default).

## More Info

| Doc | Who |
|-----|-----|
| [AGENTS.md](AGENTS.md) | Agents (first ship getting started) |
| [BEDSIDE.md](BEDSIDE.md) | Operator domain notes (metal); pin [Bedside](https://github.com/tig/bedside) via vendored contract |
| [specs/tenets.md](specs/tenets.md) | Tenets |
| [specs/lexicon.md](specs/lexicon.md) | Phrase book (GCU, spine, host-honest, Help the operator, …) |
| [specs/gcu-codenames.md](specs/gcu-codenames.md) | Public GCU codenames |
