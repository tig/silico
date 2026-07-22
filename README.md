![Silico - Prompt for metal](docs/hero.jpg)

**Prompt for metal.**

Silico makes building maintainable firmware for embedded devices simple. Given a device spec, it first guides AI agents to scaffold a Github repository setup for long-term maintainability. Agents then loop to engineer robust firmware, unit and smoke tests, a simulator, ci/cd using both real devices and the simulator, and an end-user instal/upgrade tool.

The human interface is a coding agent; not an installation guide or shell tutorial. 

## Gettings Started 

First, you need a spec for your device (which Silco calls GCUs). See these repos for example specs that will give you some idea of what's in a spec useful to Silico:

- [Xuss](tig/xuss) - A demo device based on the [M5Stack M5GO IoT Starter Kit v2.7](https://shop.m5stack.com/products/m5go-iot-starter-kit-v2-7), using [MicroPython](https://github.com/micropython). Intentionally specifies a simple implementation using Python to illustrate that path.
- [Xuss-C](tig/xuss-c) - A demo device based on the [M5Stack M5GO IoT Starter Kit v2.7](https://shop.m5stack.com/products/m5go-iot-starter-kit-v2-7), using C and native ESP32 development. Intentionally specifies a more sophisticated implementation with higher performance and usability to illustrate that path.
- [Xuss-Lame](tig/xuss) A demo device based on the [M5Stack M5GO IoT Starter Kit v2.7](https://shop.m5stack.com/products/m5go-iot-starter-kit-v2-7), that is **intentionally** under-specified. This demonstrates Silco's ability to interview the human to refine the spec and requirements interactively. 

Get the spec into a Github Repo you control. 

### Using an Agent TUI (Claude Code, Grok Build, Codex, Github Copilot CLI, ...)

* Clone the repo that contains your spec
* `cd` into that repo
* Start your favorite Agent TUI

### Using an Agent GUI (Cursor, Claude code, Github Colpilot App, ChatGPT app, ...)

* Start a new project using the Agent GUI's method for doing so.
* Point the project at your Github repo with the spec in it.

### Say GO!

Paste this prompt and hit ENTER.

```md
See https://github.com/tig/silico. Follow the getting started instructions for agents.
```

The agent owns the host path: prerequisites, GitHub setup, scaffolding, testing, device discovery, deployment, and verification. 

You own the product judgment and confirm physical or irreversible actions. 

## We work backwards from this:

> With just Claude Code on my Mac, I had the device working end-to-end the next day, and in a potential customer's hand the day after that. Silico is now a foundational piece of our company's technology.

Agents write the firmware. You own the judgment.

A **GCU** (General Contact Unit) is one shippable edge product. Silico is the spine those products pin on the host - not the product itself.

## Supported platforms (host spine)

Same operator verbs (`doctor`, `wait-device`, `inspect`, `deploy`, `gate`, …). Runtime is selected in `silico.toml` / plate.

| MCU class | Device runtime | First flash | App update | Plate |
|-----------|----------------|-------------|------------|--------|
| **RP2040-class** | MicroPython | UF2 (once) | `mpremote` file copy | `silico scaffold .` (default `gcu`) |
| **ESP32-class** | MicroPython | esptool (once) | `mpremote` file copy | default `gcu` + ESP board pin |
| **ESP32-class** | **C / ESP-IDF** | esptool / `idf.py flash` | same image path | `silico scaffold . --plate gcu-c` |

Default for new GCUs remains **MicroPython**. C on ESP-IDF is opt-in when a product needs native firmware against the same host path.

### Not silico dual-runtime paths (yet)

These may appear *inside* a GCU’s own tree; they are **not** first-class silico plates or `[runtime].language` values:

- **Arduino** core / `arduino-cli` as the Day 1 deploy backend ([issue #59](https://github.com/tig/silico/issues/59)).
- **PlatformIO** as the silico deploy path.
- **Pico SDK (C)** as a silico language peer (only if an RP2040 GCU forces it later).
- **`language = cpp`** as a third peer next to MicroPython and C (C++ may live in ESP-IDF board TUs; host-gated domain stays portable C by default).

## More Info

| Doc | Who |
|-----|-----|
| [AGENTS.md](AGENTS.md) | Agents (Day 1 getting started) |
| [BEDSIDE.md](BEDSIDE.md) | Operator domain notes (metal); pin [Bedside](https://github.com/tig/bedside) via vendored contract |
| [specs/wb-2026-fall-three-gcus.md](specs/wb-2026-fall-three-gcus.md) | Humans: v1 PR + FAQ |
| [specs/tenets.md](specs/tenets.md) | Tenets |
| [specs/lexicon.md](specs/lexicon.md) | Phrase book (GCU, spine, host-honest, Help the operator, …) |
| [specs/silicov1.md](specs/silicov1.md) | v1 build spec |
| [specs/gcu-codenames.md](specs/gcu-codenames.md) | Public GCU codenames |
