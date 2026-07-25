# Changelog

## 0.2.0

Breaking. Vendored consumers should read the migration notes before re-vendoring.

### Breaking

1. Rubric ids renumbered. Old `R4` through `R9` are now `R5` through `R10`. `R4` and `R11` are new. The invariant that rule `Rn` scores tenet `n` still holds.
2. `meta.toml` key `principles` is now `tenets`. A fixture still carrying the old key fails with exit 30 rather than being ignored, because an unrecognized key leaves the focus list empty, and an empty focus list means "score against every tenet".
3. Unknown tenet ids in `meta.toml` are rejected. Previously an id such as `R12` sat in the focus list, was never scored, and let a failing transcript report ok.
4. `bedside eval --json` emits `tenets` instead of `principles`.
5. Python API renamed with no aliases: `PRINCIPLE_IDS` to `TENET_IDS`, `ScoreReport.principle_pass` to `.tenet_pass`, `FixtureMeta.principles` to `.tenets`, `overall_from_principles` to `overall_from_tenets`.

### Migration

Renaming the key alone is not enough, because the ids moved in the same release. Remap first, then rename:

```text
principles = ["R4"]   ->   tenets = ["R5"]      # explicit human acts
principles = ["R5"]   ->   tenets = ["R6"]      # first-run owned
principles = ["R6"]   ->   tenets = ["R7"]      # scary surfaces
principles = ["R7"]   ->   tenets = ["R8"]      # confirm in their words
principles = ["R8"]   ->   tenets = ["R9"]      # no cliff
principles = ["R9"]   ->   tenets = ["R10"]     # leave-behind
```

`R1` through `R3` are unchanged. `R4` (no silent work) and `R11` (compound, but ask first) are new and have no predecessor.

### Added

1. Tenet 4, "No silent work": long or delegated work shows progress, an estimate, or per-worker status. Scored as `R4`.
2. Tenet 11, "Compound what you learn": notice friction, and with the operator's go-ahead file it upstream. Scored as `R11`, consent half only; whether the agent noticed anything worth filing stays judge-only.
3. Surface pattern for progress and status, including the five-second threshold.
4. Fixtures: `known-bad/silent-work`, `known-good/visible-progress`, `known-bad/filed-without-asking`, `known-good/compound-with-consent`.

### Changed

1. Wording pass across all tenets: present tense, one idea each, no jargon needing a glossary.
2. "Day 2" retired. The tenet is now "Teach only what tomorrow requires" and the artifact is the "leave-behind".
3. "Principles" is "tenets" throughout the prose.
4. The optional scorecard is the first-run scorecard and gained an item for status visibility.

## 0.1.2

Initial published CLI: `init`, `doctor`, `eval`, `ask`, `step`. Three layer artifacts, vendor-copy, multi-root fixtures, rule-based `R1` through `R9`.
