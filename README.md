# silico

**Prompt for metal.**

Silico is an open host-side spine for edge products built by AI agents. It scaffolds a testable firmware repository, proves changes on the host, identifies the intended device, refuses unsafe writes, deploys the application, and verifies what is actually running on the device.

The human interface is a coding agent; not an installation guide or shell tutorial. To start, open your coding agent and say:

`See https://github.com/tig/silico. Follow the getting started instructions for agents.`

The agent owns the host path: prerequisites, GitHub setup, scaffolding, testing, device discovery, deployment, and verification. You own the
product judgment and confirm physical or irreversible actions. 

Silico v1 targets RP2040-class devices running MicroPython. The spine is designed to add other GCU platforms and runtimes—including Arduino-class plates—when real products force them.

Agents write the firmware. You own the judgment.

## We work backwards from this:

> With just Claude Code on my Mac, I had the device working end-to-end the next day, and in a potential customer's hand the day after that. Silico is now a foundational piece of our company's technology.

Agents write the firmware. You own the judgment.

A **GCU** (General Contact Unit) is one shippable edge product. Silico is the spine those products pin on the host - not the product itself.

| Doc | Who |
|-----|-----|
| [AGENTS.md](AGENTS.md) | Agents (Day 1 getting started) |
| [BEDSIDE.md](BEDSIDE.md) | Operator domain notes (metal); pin [Bedside](https://github.com/tig/bedside) via vendored contract |
| [specs/wb-2026-fall-three-gcus.md](specs/wb-2026-fall-three-gcus.md) | Humans: v1 PR + FAQ |
| [specs/tenets.md](specs/tenets.md) | Tenets |
| [specs/lexicon.md](specs/lexicon.md) | Phrase book (GCU, spine, host-honest, Help the operator, …) |
| [specs/silicov1.md](specs/silicov1.md) | v1 build spec |
| [specs/gcu-codenames.md](specs/gcu-codenames.md) | Public GCU codenames |
