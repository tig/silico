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

**The developer or CI machine** (Mac, Windows, Linux runner). The Silico simulator, OSS embedded tooling, test infrastructure, and deploy tools all run on the host—not on the board.

### Spine

The shared **host tooling and contracts** Silico provides (deploy, host gate, plate, agent docs). More than one [GCU](./specs/lexicon.md#gcu) can [pin](./specs/lexicon.md#pin) it. The spine is not the product; each GCU is.

### Plate

The **template** [GCU](./specs/lexicon.md#gcu) repo layout and conventions (folders, `AGENTS.md`, `silico.toml`, CI workflows). Scaffolding a GCU means following the plate. The default is MicroPython.

### Scaffold

The act of **laying down the [plate](./specs/lexicon.md#plate)** into a product checkout: `./AGENTS.md`, standard folders, `silico.toml`, host [pin](./specs/lexicon.md#pin), [HAL](./specs/lexicon.md#hal)/sim stubs, and CI hooks.

## Getting Started

### Step 0: Prerequisites (device first)

Silico ships maintainable firmware and host tooling for a real product board. It does not invent your PCB or your domain moat.

Before you start:

1. **Get the device engineered** (or use a known board kit). You need physical metal you can plug in over USB—custom hardware, a prototype, or a starter kit such as the M5GO used in the examples below. Silico proves software on that board; it is not the schematic/layout CAD loop.
2. **Know what the product must do.** Rough is fine. Agents will interview you to refine the [spec](./specs/lexicon.md#spec); they will not invent vertical product judgment.
3. **A Mac or PC**, a **GitHub** account, and access to a **coding agent** (TUI or GUI). The agent installs host tools (Git, Python, `gh`, and so on) with your consent—you do not need a clean embedded workstation up front.

### Step 1: The Spec

Put the specification for the device—hardware and end-user functionality—in a GitHub repo. These example repos each contain a [spec](./specs/lexicon.md#spec) that has been proven to work with Silico:

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

With Silico, the agent will guide/interview the human along the way until the [first ship](./specs/lexicon.md#first-ship) is complete.

Silico ensures the agent has great [bedside manners](https://github.com/tig/bedside), and any tooling required on the [host](./specs/lexicon.md#host) will be upgraded or installed (with the operator's consent). This includes the GitHub CLI (`gh`).

When [first ship](./specs/lexicon.md#first-ship) is complete, the following will be on the default branch (e.g. `main`) of the repo (following whatever contribution standards it already uses):

* `./AGENTS.md` - The self-improving Silico agent guidance.
* `./firmware` - The device firmware that implements the spec and has been proven on real metal.
* `./sim` - The bespoke [HAL](./specs/lexicon.md#hal) and [simulator](./specs/lexicon.md#sim) used to verify the firmware on the host and in CI.
* `./install` - The install and upgrade tool end users can use to install and upgrade the firmware on the GCU.
* `.github/workflows/ci.yml` - A GitHub workflow that runs on `push` and `pull_request` and tests and validates the firmware.
* Other files and folders required for the GCU to implement the GCU spec.

### Steps 4-n: Iterate and Improve

Use AI agents to refine the GCU. E.g.:

```
Create a new PR to lower the volume of the bootup sound by 10%.
```

Each push to `main` or PR merge will cause CI workflows to run with validation and regression testing using the bespoke simulator Silico helps create.

Anytime a new agent session is started in the repo, the guidance in `./AGENTS.md` will ensure the agent continues to leverage Silico in improving the GCU.

## Real World Examples

Silico was built and improved while engineering the firmware and software for these real-world [GCUs](./specs/lexicon.md#gcu).

* **Zakalwe** - A closed-loop control module that upgrades classic BMW, Volvo, and Mercedes cars from the '80s, by [Holy Grail Labs](https://www.holygraillabs.com). This device has no internet connectivity and replicates a 1970s-era control device containing more than 100 discrete logic parts. RP2040-class board; firmware is MicroPython.
* **Quilan** - A solar-powered field logger with environmental and atmospheric sensors and LoRaWAN cloud connectivity. ESP32-class board; firmware is C.
* **Sma** - A tiny, battery-powered, sleep-friendly remote sensing and mesh-connected device. RP2040-class board; firmware is MicroPython.

Humans who use Silico to build products are encouraged to submit PRs to have their examples added above.

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
