# Bedside

Most agent docs answer: *What is this codebase?*

**Bedside** answers: *How do you treat the human in the loop?*

> **Bedside** is a standard for AI agents that operate tools for smart, high-judgment non-experts. Manners you can ship and test, not only write.

I pulled this out of real operator-care work in [silico](https://github.com/tig/silico) (Help the operator / bedside manners) so other projects can pin it instead of reinventing soft prose.

## Three artifacts

1. [`contract/`](contract/): normative rules, anti-patterns, and an `AGENTS.md` stub.
2. [`surface/`](surface/): CLI and product patterns that encode manners in tools.
3. [`eval/`](eval/): rubric, scorecard, and known-bad / known-good fixtures.

Read them in order if you are new. Pin a tag or commit of this repo.

| Start here if you | Path |
|-------------------|------|
| Write agent docs | [`contract/`](contract/) |
| Build CLIs or host tools | [`surface/`](surface/) |
| Score sessions or wire CI | [`eval/`](eval/) |

## Who the operator is

The operator is smart and high-judgment in their domain (product, hardware, clinical, field, business). They are often low literacy in the agent's tools: Git, shells, package managers, serial ports, cloud consoles, agent UIs.

They own judgment and confirmation. They do not need to be examined, shamed, or handed a wall of unexplained commands.

## What Bedside is not

- Not an end-customer product UX (different persona).
- Not a second codebase map (`AGENTS.md` still owns layout and build rules).
- Not a demand that power users abandon shortcuts they already know.

## Tenets (summary)

Normative text lives in [`contract/`](contract/). Summary only:

1. Assume low ops literacy, high judgment.
2. No walls of shell or choice.
3. Prefer doing over instructing.
4. No silent work.
5. Human acts are explicit and dumb-simple.
6. Own first-time setup from zero.
7. Own scary surfaces in plain language.
8. Confirm what they can see, in their words.
9. Never leave them at a cliff.
10. Teach only what tomorrow requires.
11. Compound what you learn.

## Adoption checklist

Claim "we follow Bedside" when:

1. **Contract:** agent-visible pin or link to [`contract/`](contract/); tenets non-negotiable on the operator path.
2. **Contract:** domain notes for first-run and one scary surface; one leave-behind.
3. **Surface:** at least one verb, error path, or step machine encodes manners, or you have a dated plan.
4. **Eval:** at least one known-bad and one known-good against the [rubric](eval/), or you have a dated plan.

Layer checklists: [contract](contract/README.md#contract-adoption) · [surface](surface/README.md#surface-checklist) · [eval](eval/README.md#eval-checklist).

## Domain packs

Tenets are universal. Examples are not.

A domain pack adds persona notes, first-run paths, scary-surface glossaries, verbs, and fixtures. It does not rewrite the tenets.

Illustration: embedded / host-first metal in [silico](https://github.com/tig/silico).

Other pack examples: blog post managment, cloud first-deploy, data/ML bootstrap, on-prem appliance bring-up.

## CLI (minimal Python)

Agent-first verbs for pin, adoption health, and rubric eval. Command logic is UI-agnostic under `src/bedside/commands/` so a future [tui-cs/cli](https://github.com/tig) front-end can replace the argparse adapter without rewriting behavior.

Requires Python 3.11+.

```bash
# from this repo
pip install -e ".[dev]"

bedside init --pin v0.2.0
# consumer (vendor-copy, no submodule):
# bedside init --vendor-from /path/to/tig/bedside --force
bedside doctor
bedside eval                    # fixture_paths from bedside.toml (multi-root)
bedside eval path/to/fixture
bedside eval third_party/bedside/eval/fixtures eval/fixtures
bedside eval --json eval/fixtures
bedside ask --id confirm-deploy --prompt "Deploy now?" --choices yes,no --default no --answer no
bedside step --id plug-usb --prompt "Plug the data USB cable." --expect "Power LED on." --confirm
```

| Verb | Job | Exit codes |
|------|-----|------------|
| `init` | Write `bedside.toml`, domain notes, `AGENTS.md` stub; optional `--vendor-from` copy | 0 ok; 30 setup |
| `doctor` | Plain-language adoption check (config, contract on disk, AGENTS, notes) | 0 ok; 30 setup |
| `eval` | Score fixture dir(s) against R1-R11; assert `expect` in meta.toml | 0 ok; 20 manners mismatch; 30 setup |
| `ask` | One structured yes/no or multi-choice operator gate (recommended first) | 0 any valid choice; 10 still needed; 30 setup |
| `step` | One human body/browser act, then confirm in their words | 0 confirmed; 10 declined/needed; 30 setup |

Exit codes (stable for agents; this vendored tree includes silico#84):

| Code | Meaning |
|------|---------|
| 0 | OK — any valid ask choice (recommended or not), or confirmed step. Read `choice=` / `matched_recommended`. |
| 10 | Human action still needed (no answer yet / empty / non-TTY without `--answer`), or step declined |
| 20 | Manners fail (`eval` expect mismatch) |
| 30 | Tool or setup error |

Do **not** treat exit 0 + `matched_recommended=false` as declined. That is an explicit alternate fork (e.g. scary yes when default is no). Halt on the safe decline label for that gate, not merely because the choice was not recommended.

**Agent Consumers:** prefer vendor-copy under `third_party/bedside` (see [docs/adopting.md](docs/adopting.md)). Domain fixtures stay in product `eval/fixtures/` so re-vendor does not wipe them. Submodule works too if you already use it.

Eval summary lines: `failed=` is focus tenets only; non-focus misses print as `info=` (for example `info=R10` when expect still matches).

```bash
pytest -q
```

## Repo layout

```text
README.md           # this index
CHANGELOG.md        # breaking changes + migration
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

v0.2. Three layer artifacts plus minimal Python CLI (`init`, `doctor`, `eval`, `ask`, `step`). Vendor-copy, multi-root domain fixtures, rule-based eval, operator gates. Front-end is argparse; cores ready for tui-cs/cli later.

v0.2 renumbers the rubric ids and renames the `meta.toml` focus key. Vendored consumers: read [CHANGELOG.md](CHANGELOG.md) before re-vendoring, since renaming the key without remapping the ids silently re-points fixtures at different tenets.

Adoption: [docs/adopting.md](docs/adopting.md).

## License

Apache-2.0. See [LICENSE](LICENSE).
