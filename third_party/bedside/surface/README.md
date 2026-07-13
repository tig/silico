# Bedside: Surface

Layer 2 of 3. Product patterns that encode operator manners in tools so agents and humans are guided even when contract prose is skimmed.

| Layer | Path | Job |
|-------|------|-----|
| Contract | [`contract/`](../contract/) | Human-readable rules |
| **Surface** | [`surface/`](.) | Tools encode manners (this artifact) |
| Eval | [`eval/`](../eval/) | Manners cannot rot |

Without surface work, Bedside is doctrine agents may ignore. Without the [contract](../contract/), surface copy has no normative bar. Without [eval](../eval/), surface quality can rot unnoticed.

This repo ships a minimal Python CLI (`bedside init|doctor|eval`) as a first surface. Command cores are UI-agnostic for a future tui-cs/cli front-end; see the [root README](../README.md#cli-minimal-python).

## Purpose

The contract says *what* good operator care is. The surface is *where* it ships:

- CLI and TUI verbs and flags.
- Error messages and exit codes.
- Guided multi-step flows (especially body and browser acts).
- Discovery UIs (ports, accounts, devices, clusters).
- Docs generators that leave a Day-2 path.

Design for smart, high-judgment non-experts and for the agents driving the tools on their behalf.

## Core patterns

### 1. Guided verbs

Thin, scriptable commands with operator-facing messages (not only machine logs).

| Verb (examples) | Intent |
|-----------------|--------|
| `doctor` | Check host, tool, or device readiness; report in plain language; exit non-zero with recovery hints |
| `first-run` / `flash-first` | Own first-time setup from zero once; detect blank vs ready |
| `deploy --verify` | Deploy then prove identity or version; fail closed on mismatch |
| `gate` | Named host proof of done (tests or sim); green means claimable |

Agents should prefer these verbs over assembling ad-hoc shell walls. Humans should be able to re-run one documented verb on Day 2.

### 2. Step machines (human body or account)

When the path requires the operator's body or browser:

```text
action → wait → confirm in their words → next
```

Rules:

1. One physical or click instruction at a time.
2. Name the control, window, or label exactly.
3. Block progress until confirmation (or a clear timeout and re-prompt).
4. Never batch "do A, B, C, then tell me."

Maps to contract principles 4, 7, and 8.

### 3. Candidate listing (plain language)

For multi-candidate scary surfaces (serial ports, kube contexts, cloud projects, USB devices):

1. List candidates with plain-language likelihood ("likely the board", "likely a different adapter").
2. Prefer explicit IDs over blind `auto` when more than one candidate exists.
3. On failure, say what you will try next. Do not shame the operator.

Maps to contract principle 6.

### 4. Fail closed and recovery

| Bad surface | Bedside surface |
|-------------|-----------------|
| Stack trace as the product UX | Short failure reason plus what to do next |
| Warning then continue on identity mismatch | Fail closed; explicit override only if safe and documented |
| "Error: failed" with no recovery | Numbered recovery steps the agent can drive or the human can do |

Exit codes should be stable enough for agents. Messages should be stable enough for operators.

### 5. Anti-walls

Tools and agent wrappers should not make a bulk "run these N commands" dump the primary UX.

Prefer:

1. One verb that orchestrates.
2. Or one command at a time with explanation, run by the agent when possible.

If a tool must print a command for the human to paste (for example a browser device code), print that one string with context. Not five unlabeled blocks.

Maps to contract principles 2 and 3.

### 6. Day-2 leave-behind

After success, the surface (or the docs it generates) leaves one routine path:

1. One update, deploy, or verify command (or short script).
2. What "good" looks like (LED pattern, health URL, version string).

No textbook of equivalent alternatives.

Maps to contract principle 9.

## Agent-first CLI notes

Surfaces that agents drive should:

1. Be non-interactive by default when flags can replace prompts.
2. Use clear exit codes (0 success; non-zero classes for retry vs human-needed vs hard fail).
3. Print operator prose on stderr or a dedicated summary stream; keep machine-readable output optional (`--json`) without making JSON the only recovery path.
4. Refuse or loudly warn on dangerous blind defaults (for example auto-pick among many devices).

Interactive TUIs are fine for humans. Agents need a scriptable path to the same manners.

## Domain packs (surface side)

Domain packs supply verbs, copy, and step graphs. Not new principles.

| Domain | Example surface concerns |
|--------|--------------------------|
| Embedded / metal | Port discovery, first flash, BOOT/RESET steps, version verify on device |
| Cloud first-deploy | Auth device code, project or account pick, region, fail-closed IAM |
| Data / ML bootstrap | Runtime or env install, GPU checks, one re-run training or serve command |
| Appliance / on-prem | Network join, admin password once, health URL leave-behind |

Reference illustration: [silico](https://github.com/tig/silico) host path (doctor / deploy / verify style intent; implementation may lag doctrine).

## Surface checklist

- [ ] At least one guided verb or error path encodes plain-language recovery.
- [ ] First-run is a first-class path (verb or documented step machine), not folklore.
- [ ] Multi-candidate discovery lists plain-language candidates; avoids blind auto when unsafe.
- [ ] Fail closed on identity or verify mismatches (or documented exception).
- [ ] Success leaves one Day-2 command and what "good" looks like.

Contract pin: [`contract/`](../contract/). Prove manners: [`eval/`](../eval/).
