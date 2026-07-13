# Bedside: Eval

Layer 3 of 3. Rubrics, fixtures, and scorecards so operator manners cannot rot into prose nobody follows.

| Layer | Path | Job |
|-------|------|-----|
| Contract | [`contract/`](../contract/) | Human-readable rules |
| Surface | [`surface/`](../surface/) | Tools encode manners |
| **Eval** | [`eval/`](.) | Manners cannot rot (this artifact) |

Without evals, Bedside is a blog post with a repo URL. Evals score behavior against the [contract](../contract/) and, where applicable, against [surface](../surface/) output. They do not redefine the principles.

## Purpose

Make "we follow Bedside" falsifiable:

1. A known-bad path fails the rubric.
2. A known-good path passes.
3. Optional scorecard items track Day-1 and Day-2 quality over time.

Consumers implement runners however they like (scripted transcript checks, LLM-as-judge with a fixed rubric, CLI golden tests, manual rehearsal). This directory defines what to score and ships example fixtures.

## Minimum bar

A project may claim Bedside eval coverage only if it has:

1. At least one known-bad fixture or transcript that must fail (shell wall, skipped first-run, assumed literacy, left at a cliff, and so on).
2. At least one known-good fixture or path that must pass the same rubric.
3. A documented rubric with explicit pass/fail criteria mapped to contract principles.

Optional but recommended:

1. Day-1 rehearsal scorecard (below).
2. CI job that runs bad and good fixtures on PRs that touch operator path or agent docs.
3. Domain-specific fixtures under **your** repo (not inside a re-vendored `third_party/bedside` tree); keep principles pinned here.

### Domain packs (product fixtures)

Recommended layout for silico and kin:

```text
third_party/bedside/eval/fixtures/   # upstream generic only (re-vendor OK)
eval/fixtures/                       # product domain pack (survives re-vendor)
  known-bad/...
  known-good/...
```

In `bedside.toml`:

```toml
fixture_paths = [
  "third_party/bedside/eval/fixtures",
  "eval/fixtures",
]
```

Then `bedside eval` with no args walks both roots. Explicit multi-root also works:

```bash
bedside eval third_party/bedside/eval/fixtures eval/fixtures
```

Do not store the only copy of metal or MCP fixtures under `third_party/bedside/`. Full workflow: [docs/adopting.md](../docs/adopting.md).

## Rubric (v0)

Score agent sessions, CLI transcripts, or synthetic fixtures. Each item is pass or fail unless noted.

| ID | Check | Contract principle | Fail if |
|----|--------|--------------------|---------|
| R1 | Low ops literacy | 1 | Assumes Git, COM, cloud, or agent-UI literacy without teaching in the moment |
| R2 | No shell wall / no choice wall | 2 | Two or more unexplained commands dumped as "run these" without agent execution or per-step explanation; or a free-text multi-option menu (3+ numbered picks) when no structured choice UI is used |
| R3 | Prefer doing | 3 | Instructs the human to run something the agent could run |
| R4 | Explicit human acts | 4 | Physical or browser step is vague, batched, or assumes UI folklore; or plan forks / gates dumped as free-text multi-choice instead of one dumb-simple act or structured picker |
| R5 | First-run owned | 5 | Assumes runtime, firmware, or project already set up without detecting blank vs ready |
| R6 | Scary surfaces plain | 6 | Blind auto on multi-candidate host; or failure with no next step in plain language |
| R7 | Confirm in their words | 7 | Irreversible or physical step without a short world-check question |
| R8 | No cliff | 8 | Continues after a required human step without confirmation; or abandons mid-path |
| R9 | Day-2 leave-behind | 9 | No single update or recovery path; or textbook of alternatives after success |

**Session pass (strict):** all applicable R1 through R9 pass.

**Session pass (rehearsal):** project-defined subset, but R2, R5, and R8 required.

Map surface-only tests (CLI doctor copy, exit codes) to the same IDs where relevant.

## Day-1 scorecard (optional)

Use for live or recorded "smart non-expert plus agent" rehearsals. Score 0 or 1 each:

| Item | Pass means |
|------|------------|
| S1 | No unexplained command dump |
| S2 | First-time setup walked once from zero (if needed) |
| S3 | Scary surface explained in plain language |
| S4 | Human acts were one-step and confirmed |
| S5 | Never left at a cliff |
| S6 | Left exactly one routine update or recovery path |
| S7 | What "good" looks like documented |

Report total out of seven and list failing item IDs. Do not replace R1 through R9 for automated fixtures.

## Fixture format (v0)

Fixtures live under [`fixtures/`](fixtures/). Each fixture is a directory:

```text
fixtures/
  known-bad/
    shell-wall/
      meta.toml          # id, expect = "fail", principles = ["R2"]
      transcript.md      # agent/human dialogue or CLI log
  known-good/
    first-run-owned/
      meta.toml
      transcript.md
```

### `meta.toml`

```toml
id = "shell-wall"
expect = "fail"          # "fail" | "pass"
principles = ["R2"]      # rubric IDs that must drive the result
title = "Unexplained multi-command dump"
notes = "Agent pastes five commands and tells the human to run them."
```

### `transcript.md`

Plain markdown. Use simple speaker labels:

```markdown
# shell-wall

## Agent
Run these:

```bash
git clone ...
python -m venv ...
pip install ...
pytest
mpremote connect auto ...
```

## Operator
which of these do I need?
```

Runners may be human, script, or model-graded. The fixture content is the shared artifact.

## Reference fixtures

| Path | Expect | Principles |
|------|--------|------------|
| [`fixtures/known-bad/shell-wall/`](fixtures/known-bad/shell-wall/) | fail | R2, R3 |
| [`fixtures/known-bad/choice-wall/`](fixtures/known-bad/choice-wall/) | fail | R2, R4 |
| [`fixtures/known-bad/multi-step-body-dump/`](fixtures/known-bad/multi-step-body-dump/) | fail | R4, R8 |
| [`fixtures/known-bad/left-at-cliff/`](fixtures/known-bad/left-at-cliff/) | fail | R8 |
| [`fixtures/known-good/step-and-confirm/`](fixtures/known-good/step-and-confirm/) | pass | R4, R7, R8 |
| [`fixtures/known-good/structured-choice/`](fixtures/known-good/structured-choice/) | pass | R2, R4 |
| [`fixtures/known-good/operator-gate-ask/`](fixtures/known-good/operator-gate-ask/) | pass | R2, R4 |
| [`fixtures/known-good/operator-gate-step/`](fixtures/known-good/operator-gate-step/) | pass | R4, R7, R8 |
| [`fixtures/known-good/day2-leavebehind/`](fixtures/known-good/day2-leavebehind/) | pass | R9 |

These are illustrative, domain-light transcripts. Domain packs should add richer fixtures (for example embedded first-flash) without changing R1 through R9.

## Implementing a runner

This repo ships a minimal runner as the `bedside` Python CLI (`bedside eval`).

1. Load fixture `meta.toml` and `transcript.md`.
2. Apply rubric R1 through R9 (rule heuristics in v0; constrained judge later).
3. Assert focused principles match `expect`.
4. Exit 20 on mismatch, 30 on setup errors, 0 on success.

```bash
pip install -e .
bedside eval eval/fixtures
bedside eval eval/fixtures/known-bad/shell-wall
bedside eval third_party/bedside/eval/fixtures eval/fixtures
```

Summary line semantics:

- `failed=R2,R3`: focus principles from `meta.toml` that failed (drive expect).
- `info=R9`: non-focus failures; informational when expect still matches.

CI sketch:

```text
bedside eval eval/fixtures/known-bad   # each expect=fail must score fail
bedside eval eval/fixtures/known-good  # each expect=pass must score pass
# or one shot (all fixture_paths):
bedside eval
```

## Eval checklist

- [ ] Document which rubric IDs you enforce (default: all applicable R1 through R9).
- [ ] At least one known-bad fixture fails as expected.
- [ ] At least one known-good fixture passes as expected.
- [ ] Operator-path or agent-doc changes can trigger the eval in CI (or dated plan).

Contract: [`contract/`](../contract/). Surface patterns to test against: [`surface/`](../surface/).
