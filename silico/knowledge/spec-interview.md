# Spec interview mode (product contract quality)

**Not product domain.** Guidance for agents when a GCU’s `spec.md` is too thin or fights itself. Normative Day 1 placement: root `AGENTS.md` → **Spec interview mode**. Issue: [tig/silico#68](https://github.com/tig/silico/issues/68).

## When to fire

After operator **go**, when reading product contract files:

| Signal | Examples |
|--------|----------|
| **Thin** | Missing readiness layers, hardware fix, product face, rails, acceptance rows |
| **Contradictory** | Same key two ways; acceptance rows that cannot all be true; identity-before vs after audio |
| **Silent on scary surfaces** | Long audio, force channels, escape hatch, dead-man left open |

If the contract is good enough: **do not** interview.

## Operator paths

Prefer structured chooser (`bedside ask` / host picker):

1. **Interview now** (recommended when contradictions block a honest first slice).
2. **Proceed interactively** — build with explicit assumptions; improve `spec.md` as you go; operator may re-run the agent later to rebuild as the contract improves.
3. Adjust / stop.

## Interview manners

1. One gap or tight cluster per gate.
2. Recommended option first when plate / parts / knowledge give a default.
3. Free text only for open domain judgment.
4. Propose durable `spec.md` edits only after **yes**; else issues / ambiguity log.
5. Do not invent vertical moat without operator judgment.

## Interactive path

When the operator opts in:

1. Do not claim the product is fully specified.
2. Host-first still applies; metal still needs observe when metal is in scope.
3. Late-step spec update offers remain required (AGENTS Spec gaps).
4. Re-run later is a feature, not a failure.

## Fixture

Private **`tig/xuss-lame`**: deliberately lame contract for practice. Agents there must **not** open `tig/xuss` or `tig/xuss-c` (anti-cheat in that repo’s AGENTS).

## Anti-patterns

- Block forever on a perfect spec.
- Free-text multi-choice walls.
- Chat-only recovery when the next agent will re-guess.
- “Hardware later” with no wait-device when metal is in scope.
