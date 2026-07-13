# silico

**Prompt for metal.** Silico is an open host-side spine so AI agents can ship real edge products: prove firmware on the host before anyone trusts a flash, install and update a device a normal human can run twice, and verify version identity so the board cannot lie about what it is running. Your domain and brand stay in your app; silico is not the product, not a company SKU, and not a device-ops cult. One rule: **host gate green means done; metal confirms.**

We work backwards from this:

> With just Claude Code on my Mac, I had the device working end-to-end the next day, and in a potential customer's hand the day after that. Silico is now a foundational piece of our company's technology.

Agents write the firmware. You own the judgment.

A **GCU** (General Contact Unit) is one shippable edge product. Silico is the spine those products pin on the host - not the product itself.

## Install (host only)

Prefer an immutable tag:

```text
python -m pip install "silico @ git+https://github.com/tig/silico.git@v0.1.0"
```

```text
silico doctor
silico scaffold ./my-gcu
cd my-gcu && python -m pip install -r requirements-dev.txt && python -m pytest -q
```

Device writes require **explicit operator confirmation** (`silico deploy … --yes` only after a clear yes). Agents must **poll USB** (`silico wait-device`) instead of asking humans to announce plug-in.

| Verb | Role |
|------|------|
| `silico doctor` | Host env + scored serial ports (read-only) |
| `silico wait-device` | Poll until preferred board appears |
| `silico inspect` | Non-destructive device inspect |
| `silico deploy … --yes --verify` | Write files only with confirmation; version check |
| `silico scaffold` | Versioned GCU plate |

## Docs

| Doc | Who |
|-----|-----|
| [AGENTS.md](AGENTS.md) | Agents (Day 1 getting started) |
| [specs/wb-2026-fall-three-gcus.md](specs/wb-2026-fall-three-gcus.md) | Humans: v1 PR + FAQ |
| [specs/tenets.md](specs/tenets.md) | Tenets |
| [specs/lexicon.md](specs/lexicon.md) | Phrase book |
| [specs/silicov1.md](specs/silicov1.md) | v1 build spec |
| [specs/gcu-codenames.md](specs/gcu-codenames.md) | Public GCU codenames |

Agent prompt to start: `See https://github.com/tig/silico. Follow the getting started instructions for agents.`
