# BEDSIDE.md (silico metal domain notes only)

This file is **not** a fork of the Bedside principles.

| Need | Open once |
|------|-----------|
| Portable manners (normative) | 	hird_party/bedside/contract (pin: edside.toml) |
| Silico Day 1 / CLI / plate | root AGENTS.md |
| This file | metal-host glossary only — do **not** also reload the full contract if AGENTS already pinned it |

## Metal first-run (domain pack)

Host tools and Day-1 phases live in **AGENTS.md**. Metal-specific once-only path:

1. Data USB cable (not charge-only).
2. Long silico wait-device (agent polls; human does not announce plug-in).
3. silico inspect --port COMx proves REPL, or UF2 first-flash of MicroPython **once**.
4. Operator confirms this port is the product board before any write.
5. App updates after that: no re-teaching UF2.

Do **not** stop Day 1 after host gate green unless the operator explicitly defers metal.

## Scary surfaces (metal glossary)

| Surface | Plain language |
|---------|----------------|
| USB serial / COM | Prefer explicit COMx; demote CH340 and Debug Probe; never blind connect auto on multi-device hosts |
| Deploy overwrite | Inspect first; write only with operator yes (silico deploy --port COMx --yes, usually [deploy].core) |
| Board identity | High score is a hint; confirm product board in their words |
| After reset | Port may re-enumerate; re-discover before reuse |

## Day-2 leave-behind (metal)

`	ext
pytest -q
silico deploy --port COMx --yes --verify
`

Good: host gate green; device FW_VERSION matches host; documented LED/status.

## Customer 0 → tig/bedside

Portable manners gaps (contract, surface, edside CLI, eval): file **tig/bedside**, do not soft-fork principles here.
Metal/host-spine gaps: fix **tig/silico**.
