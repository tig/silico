# Adopting Bedside (consumers)

How silico, mcec, or any product repo should pin Bedside so agents see it, CI can score it, and refreshes do not eat domain work.

## Recommended layout

```text
your-product/
  AGENTS.md                    # Bedside stub + domain notes pointer
  BEDSIDE.md                   # domain notes only (not a principles fork)
  bedside.toml                 # pin + paths + fixture_paths
  third_party/bedside/         # VENDORED copy of tig/bedside (or submodule)
    contract/
    surface/
    eval/fixtures/             # upstream generic fixtures only
    src/                       # optional; for pip install -e third_party/bedside
    VENDOR.md                  # stamp: source path + pin SHA
  eval/fixtures/               # YOUR domain pack (survives re-vendor)
    known-bad/...
    known-good/...
```

**Rule:** product fixtures live under `eval/fixtures/` (or another path you own). Never write domain transcripts only under `third_party/bedside/`; the next vendor refresh will delete them.

## Vendor-copy workflow (preferred for CI)

Submodules need auth and init on every clone. Silico customer 0 uses a **full tree copy** under `third_party/bedside` instead.

### First time

```bash
# from your product repo; SOURCE is a local checkout of tig/bedside
pip install -e /path/to/tig/bedside   # or pip install git+https://github.com/tig/bedside.git@<sha>

bedside init --vendor-from /path/to/tig/bedside --force
# writes bedside.toml, AGENTS.md section, BEDSIDE.md
# copies contract/surface/eval/src into third_party/bedside/
# scaffolds eval/fixtures/{known-bad,known-good}/
# pin = git HEAD of source when --pin is left at default "main"
```

`bedside.toml` will look like:

```toml
pin = "198fdb7..."   # commit SHA
contract_path = "third_party/bedside/contract"
surface_path = "third_party/bedside/surface"
eval_path = "third_party/bedside/eval"
domain_notes = "BEDSIDE.md"
agents_stub = true
fixture_paths = [
  "third_party/bedside/eval/fixtures",
  "eval/fixtures",
]
```

### Refresh when upstream improves

```bash
# update your local tig/bedside checkout (fetch + checkout new tag/SHA)
bedside init --vendor-from /path/to/tig/bedside --force
# re-copies third_party/bedside; rewrites bedside.toml pin
# does not delete your product eval/fixtures/
bedside doctor
bedside eval
```

Manual alternative (no CLI): copy the same top-level trees, write `VENDOR.md` with the SHA, set `pin` in `bedside.toml`.

### Submodule alternative

Fine if your org already standardizes on submodules:

```bash
git submodule add https://github.com/tig/bedside.git third_party/bedside
cd third_party/bedside && git checkout <tag-or-sha>
bedside init --contract-path third_party/bedside/contract --force
# still put domain fixtures in product eval/fixtures/
```

## Domain fixtures (issue: metal, MCP, …)

Principles stay in vendored `contract/`. Domain packs only add transcripts:

```text
eval/fixtures/
  known-bad/
    shell-wall-flash/
      meta.toml          # expect = "fail", principles = ["R2", "R3"]
      transcript.md
  known-good/
    first-flash-walked/
      meta.toml
      transcript.md
```

Same shape as upstream `eval/fixtures`. Rubric IDs stay R1-R9.

### Multi-root eval

```bash
# explicit (always works)
bedside eval third_party/bedside/eval/fixtures eval/fixtures

# default: all roots listed in bedside.toml fixture_paths
bedside eval
```

Missing empty domain dirs are skipped if not present; empty `known-bad/` with no `meta.toml` contributes zero fixtures.

## Eval log lines

Focus principles come from each fixture's `meta.toml` `principles` list.

- `failed=R2,R3`: focus principles that failed (drive expect).
- `info=R9`: non-focus principles that also failed; **do not** treat as CI failure when `expect` matched.

Example OK line after the UX fix:

```text
[OK] step-and-confirm expect=pass scored=pass info=R9
```

## Install CLI from vendored tree

```bash
pip install -e third_party/bedside
# or pin from GitHub:
# pip install git+https://github.com/tig/bedside.git@<sha>
```

## Checklist

1. Vendor or submodule so `contract_path` exists.
2. `bedside.toml` pin is a tag or SHA (not floating `@main` in production).
3. Domain notes in `BEDSIDE.md` / `AGENTS.md`.
4. Domain fixtures under product `eval/fixtures/`.
5. CI: `bedside doctor` and `bedside eval`.
