# Bedside

Most agent docs answer: *What is this codebase?*

**Bedside** answers: *How do you treat the human in the loop?*

> **Bedside** is a standard for AI agents that operate tools for smart, high-judgment non-experts. Manners you can ship and test, not only write.

I pulled this out of real operator-care work in [silico](https://github.com/tig/silico) (Help the operator / bedside manners) so other projects can pin it instead of reinventing soft prose.

## Three artifacts

Bedside is not one essay. It is three directories:

1. [`contract/`](contract/): normative rules, anti-patterns, and an `AGENTS.md` stub.
2. [`surface/`](surface/): CLI and product patterns that encode manners in tools.
3. [`eval/`](eval/): rubric, scorecard, and known-bad / known-good fixtures.

Read them in order if you are new. Pin a tag or commit of this repo. Do not soft-fork the principles into a kinder local copy.

| Start here if you | Path |
|-------------------|------|
| Write agent docs | [`contract/`](contract/) |
| Build CLIs or host tools | [`surface/`](surface/) |
| Score sessions or wire CI | [`eval/`](eval/) |

## Who the operator is

The operator is smart and high-judgment in their domain (product, hardware, clinical, field, business). They are often low literacy in the agent's tools: Git, shells, package managers, serial ports, cloud consoles, agent UIs.

They own judgment and confirmation. They do not need to be examined, shamed, or handed a wall of unexplained commands.

Some projects call this person Grady-shaped. Use whatever name fits. Bedside is the contract; the codename is optional.

## What Bedside is not

- Not "be friendly" or generic politeness.
- Not end-customer product UX (different persona).
- Not a second codebase map (`AGENTS.md` still owns layout and build rules).
- Not a demand that power users abandon shortcuts they already know.

Bedside is operator care for the host path: setup, tools, deploys, recoveries. Anything where a smart non-expert can get stranded.

## Principles (summary)

Normative text lives in [`contract/`](contract/). Summary only:

1. Assume low ops literacy, high judgment.
2. Do not dump a wall of shell.
3. Prefer doing over instructing.
4. Human acts: explicit, one step, dumb-simple.
5. Own first-time setup from zero.
6. Own scary surfaces in plain language.
7. Confirm in their words before irreversible or physical steps.
8. Never leave them at a cliff.
9. Teach only what Day 2 requires.

## Adoption checklist

Claim "we follow Bedside" when:

1. **Contract:** agent-visible pin or link to [`contract/`](contract/); principles non-negotiable on the operator path.
2. **Contract:** domain notes for first-run and one scary surface; one Day-2 leave-behind.
3. **Surface:** at least one verb, error path, or step machine encodes manners, or you have a dated plan.
4. **Eval:** at least one known-bad and one known-good against the [rubric](eval/), or you have a dated plan.

Layer checklists: [contract](contract/README.md#contract-adoption) · [surface](surface/README.md#surface-checklist) · [eval](eval/README.md#eval-checklist).

## Domain packs

Principles are universal. Examples are not.

A domain pack adds persona notes, first-run paths, scary-surface glossaries, verbs, and fixtures. It does not rewrite the nine principles.

Illustration: embedded / host-first metal in [silico](https://github.com/tig/silico).

Other pack shapes: cloud first-deploy, data/ML bootstrap, on-prem appliance bring-up.

## CLI (minimal Python)

Agent-first verbs for pin, adoption health, and rubric eval. Command logic is UI-agnostic under `src/bedside/commands/` so a future [tui-cs/cli](https://github.com/tig) front-end can replace the argparse adapter without rewriting behavior.

Requires Python 3.11+.

```bash
# from this repo
pip install -e ".[dev]"

bedside init --pin v0.1.0
bedside doctor
bedside eval                    # default: eval/fixtures when present
bedside eval path/to/fixture
bedside eval --json eval/fixtures
```

| Verb | Job | Exit codes |
|------|-----|------------|
| `init` | Write `bedside.toml`, `BEDSIDE.md` domain scaffold, `AGENTS.md` stub | 0 ok; 30 setup |
| `doctor` | Plain-language adoption check (config, contract on disk, AGENTS, notes) | 0 ok; 30 setup |
| `eval` | Score fixture dir(s) against R1-R9; assert `expect` in meta.toml | 0 ok; 20 manners mismatch; 30 setup |

Exit codes (stable for agents):

| Code | Meaning |
|------|---------|
| 0 | OK |
| 10 | Human action needed (reserved) |
| 20 | Manners fail (`eval` expect mismatch) |
| 30 | Tool or setup error |

`init` does not run `git submodule` for you. Vendor or submodule `tig/bedside` so `contract_path` exists, then `doctor`.

```bash
pytest -q
```

## Repo layout

```text
README.md           # this index
LICENSE             # Apache-2.0
pyproject.toml      # bedside package
src/bedside/        # CLI + eval engine
tests/
contract/           # layer 1: rules
surface/            # layer 2: product patterns
eval/               # layer 3: rubric + fixtures
  fixtures/
    known-bad/
    known-good/
```

## Status

v0.1. Three layer artifacts plus minimal Python CLI (`init`, `doctor`, `eval`). Rule-based eval only. Front-end is argparse; cores ready for tui-cs/cli later.

Issues and PRs welcome for clearer principles, domain packs, stronger eval rules, more fixtures, and `BEDSIDE.md` conventions.

## License

Apache-2.0. See [LICENSE](LICENSE).
