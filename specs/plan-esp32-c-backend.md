# Plan: ESP32 C / ESP-IDF backend (issue #53)

**Status:** Implementation plan (not yet built).  
**Issue:** [tig/silico#53](https://github.com/tig/silico/issues/53) — *Enable ESP32 development in C in addition to the current Python*.  
**First test case:** [tig/xuss-c](https://github.com/tig/xuss-c) — C twin of [tig/xuss](https://github.com/tig/xuss); M5GO / classic ESP32; host CTest already green on pure `src/` + `include/`.  
**Related:** [tig/silico#57](https://github.com/tig/silico/issues/57) (MicroPython ESP32 Day 1 gaps — do first), [tig/silico#50](https://github.com/tig/silico/issues/50) (Xuss product), [silicov1.md](./silicov1.md), root `AGENTS.md`, `BEDSIDE.md`.

---

## 0. One-sentence goal

Make a C/ESP-IDF GCU feel like a MicroPython GCU on the operator path: same verbs (`doctor`, `wait-device`, `inspect`, `deploy`, `gate`, `product-path`), same identity/protocol contracts, different toolchain underneath — proven on **xuss-c** before anyone claims Grady's S3 path is "C-ready."

---

## 1. Why this exists (and what it is not)

### 1.1 Motivation (from #53)

Customer zero (Grady / Quilan-shaped) asked whether silico can do **both C and MicroPython**, driven by a solar/battery power story. Sleep current dominates duty-cycled budgets; language only touches awake milliseconds. The honest advice remains **Python first, measure, then C if the measurement says so** — but that advice is only honest if switching later is a **backend swap**, not a rewrite.

The contracts are already language-agnostic. Only the plumbing is Python today:

| Contract (language-agnostic) | Python plumbing today |
|------------------------------|------------------------|
| Identity on the link | mpremote + `version.py` import / print |
| ASCII protocol, get/set/save/defaults, escape hatch | product firmware (any language can speak it) |
| Host-first seam + product-path honesty | CPython import + AST `machine` allowlist + pytest defaults scan |
| Deploy + verify | mpremote file copy; UF2 first-flash story |
| Runtime pin | `[runtime].mpy_cross` |

A C GCU that prints its identity line and answers the protocol is **indistinguishable at the port** from a Python one. That is the design working as intended.

### 1.2 Not goals

- Arduino core, PlatformIO, or C++ frameworks (one C path: **ESP-IDF** for ESP32-class; Pico SDK only later if an RP2040 GCU forces it).
- Domain Xuss voice/edge/face code living in silico (stays in `tig/xuss` / `tig/xuss-c`).
- Claiming C is required for battery life without a measured draw on the product build.
- Soft-forking Bedside principles into a second essay; metal notes stay in `BEDSIDE.md`.
- Making every existing GCU dual-language. Default plate remains MicroPython; C is opt-in plate + `silico.toml` runtime.

### 1.3 Relationship to #57 (do first)

#53 itself sequences **MicroPython-on-ESP gaps before the C backend**. #57 is that track for M5GO / classic ESP32:

1. CH9102 (and known M5 VID/PID) port scoring.
2. esptool first-flash documented next to UF2 in BEDSIDE/AGENTS (and/or a thin `silico flash` helper later).
3. `silico pull` reliability against boot banners.
4. Honest mpy pin from `sys.implementation.version`.

Those fixes unblock Grady/Xuss Day 1 **in Python**, which is still the recommendation. This plan **depends on** esptool being a first-class metal path (#57) and **adds** build-and-flash of an IDF app image as the C deploy path.

**Rule:** land #57 enough that `silico doctor` / `wait-device` / esptool first-flash notes do not lie on M5GO before declaring C Day 1 "operator complete." C deploy may land in parallel on the host side (fixtures with no board), but metal proof waits on a working ESP serial path.

---

## 2. Current state (spine vs first consumer)

### 2.1 Silico today (Python-only plumbing)

| Verb | Implementation | C-blocking assumption |
|------|----------------|----------------------|
| `scaffold` | single plate `plates/gcu` | one runtime tree |
| `deploy` | mpremote `cp` of `[deploy].core` files | file-copy model; requires mpremote |
| `inspect` | mpremote exec + optional `--apply-mpy-pin` | REPL / MicroPython version |
| `gate` / host hygiene | CPython import of deploy set + AST `machine` allowlist | Python sources only |
| `product-path` | AST scan of pytest/sim for defaults module | Python defaults module |
| `doctor` / ports | RP2040 preferred; CH340 demoted | ESP CH9102 still wrong (#57) |
| First flash docs | UF2 / BOOT / `RPI-RP2` | no esptool subsection yet (#57) |

### 2.2 xuss-c today (first test case)

Repo shape already matches the **C host-first** half of the target architecture:

```text
tig/xuss-c/
  include/xuss/     # config, edge, protocol headers (portable)
  src/              # pure C domain (edge, config, protocol)
  host/             # CMake + CTest (L0) — no IDF required
  firmware/         # placeholder; not yet a full IDF project
  spec.md           # product contract (twin of tig/xuss)
  parts.toml
```

Host gate (already the product's L0):

```text
cmake -S host -B build/host
cmake --build build/host
ctest --test-dir build/host --output-on-failure
```

Open in their own spec: *"Optional: silico host tooling bridge for C deploys (not required for L1)"* — this plan is that bridge. Xuss-C L1 can flash by hand with `idf.py`/`esptool` first; **silico Day 1 exit for C** requires the bridge.

**Board note:** #53's "done when" names ESP32-S3 (Grady). Xuss-C's board is **classic ESP32 (M5GO)**. Treat **ESP32-class under ESP-IDF** as the backend; prove on M5GO first, then re-pin target/chip for S3 without inventing a second deploy story.

### 2.3 What "same operator experience" means

Operator (and agent) still:

1. Confirms start gate → host gate green.
2. Plugs data USB → long `wait-device`.
3. `inspect` → identity verified against manifest.
4. `bedside ask` confirm-board → deploy plan without write → confirm-deploy → `--yes`.
5. Verify identity/version after flash; escape hatch (`repl`/`reboot` in product protocol) still required by product specs.

They do **not** need to know whether the image was MicroPython sources or an IDF binary once deploy is confirmed.

---

## 3. Design principles

1. **Backend, not rewrite.** Runtime selected by `silico.toml`; product contracts stay language-agnostic.
2. **Host first still means host first.** Domain logic compiles and tests on the host (CTest for C; pytest for Python). Flash confirms; it does not invent truth.
3. **One scary surface language.** Deploy still needs explicit `--port` + operator yes; plan output names the flash target in plain words.
4. **Hygiene is the allowlist, spelled differently.** Python: `machine` imports. C: device headers / ESP-IDF includes only in the board backend translation unit(s).
5. **Extract, then open.** Build the minimum spine that makes xuss-c's Day 1 honest; promote patterns from xuss-c into `plates/gcu-c` once proven, not the reverse.
6. **Do not dual-maintain product domain in silico.** Plate ships hello-metal + HAL skeleton only.

---

## 4. Target architecture

### 4.1 Runtime selection (`silico.toml`)

Extend config so tools branch on language/toolchain without guessing from file extensions alone.

```toml
[product]
name = "Xuss-C"
fw_name = "XUSSC"
fw_version = "0.0.1"

[runtime]
# Existing MicroPython plate keeps language default micropython / board pin.
language = "c"                    # "micropython" | "c"  (default: micropython)
toolchain = "esp-idf"             # only valid pairing for language = c in this plan
# Pin the IDF release the GCU builds against (string; agent + doctor check).
esp_idf = "v5.3.2"                # example; exact pin decided when plate ships
board = "m5stack-core-esp32"      # or product-local idf target name
# chip for esptool: esp32 | esp32s3 | …
chip = "esp32"

[host]
# Shell or argv form run by `silico gate` when language = c.
gate = "cmake --build build/host --target test"
# Or: gate = "ctest --test-dir build/host --output-on-failure"
product_defaults = "include/xuss/config.h"   # or src/defaults.c — see §5.4

[hal]
# C: basenames (or stems) allowed to #include freertos / driver / esp_* / soc
allow_device_headers = ["board_m5go", "hal_board"]

[deploy]
# C path: not a file list for mpremote — a build artifact recipe.
mode = "idf-flash"                # default for language=c; mpy remains file-copy
# Optional explicit binary after build (relative to repo root):
# image = "build/firmware/xuss-c.bin"
# Or rely on idf.py flash with project dir:
project = "firmware"
```

**Compat:** omitting `[runtime].language` (or `language = "micropython"`) preserves today's behavior for all existing GCUs. No silent change of deploy for Python plates.

### 4.2 Module map (new / extended)

| Piece | Role |
|-------|------|
| `silico/config_toml.py` | Read `language`, `toolchain`, IDF pin, chip, deploy mode, allow_device_headers, host gate string |
| `silico/runtime.py` (new) | Resolve active backend; fail clearly on unknown pairs |
| `silico/deploy_mpy.py` | Current mpremote deploy extracted from `deploy.py` (behavior-preserving) |
| `silico/deploy_idf.py` (new) | Plan/build/flash via idf.py / esptool; dry plan without `--yes` |
| `silico/deploy.py` | Thin dispatcher: plan/deploy → mpy or idf |
| `silico/inspect_device.py` | Branch: mpy REPL path vs **serial identity-line** path for C images |
| `silico/host_hygiene.py` or `gate_c.py` | C hygiene: no device headers outside allowlist; optional compile check of host lib |
| `silico/product_path.py` | C defaults: scan host tests for references to the defaults TU/header |
| `silico/doctor.py` | Report IDF on PATH / `IDF_PATH`, chip tools, language from toml |
| `silico/scaffold.py` | `silico scaffold . --plate gcu-c` (or `runtime=c`) |
| `silico/plates/gcu-c/` | Hello-metal C plate (HAL header, host double, IDF main stub, CMake dual target) |
| `BEDSIDE.md` / `AGENTS.md` | ESP-IDF flash + C gate notes; point to plate; do not duplicate full IDF install manual |

### 4.3 Identity and inspect (C)

Inspect must not require a MicroPython REPL.

**Device contract (already product-shaped):** on boot (or on `identity` command), the app prints a stable line, e.g.:

```text
fw_name=XUSSC fw_version=0.0.1
```

(or the same key/value family the MicroPython plate uses — **one identity grammar** for both backends.)

**Host behavior for `language = c`:**

1. Open the port at the configured baud (default 115200; toml override).
2. Soft prompt: send newline and/or `identity\n` (product protocol); do not send mpremote raw REPL sequences.
3. Parse identity line; compare to `[product].fw_name` / `fw_version`.
4. Report port scoring + identity; never write.
5. **No `--apply-mpy-pin`.** Instead optional later: `--apply-idf-pin` only if we discover IDF version from a self-report field; v1 of this plan may pin IDF only from toml/docs (agent-owned), not from device probe.

**Verify after deploy:** same identity parse after reset / re-enumerate; port may change after flash — re-discover before claiming success (BEDSIDE already: after reset, re-discover).

### 4.4 Deploy (C)

| Step | Plan (`deploy` without `--yes`) | Write (`--yes`) |
|------|----------------------------------|-----------------|
| Preconditions | `language=c`, project dir exists, port listed | same + operator yes |
| Build | Show `idf.py -C <project> build` (or cmake) command that will run | Run build; fail closed on non-zero |
| Flash | Show chip, port, app image path / `idf.py flash` | Run flash (esptool under idf.py) |
| Verify | Note identity check will run | Reset if needed; wait for port; parse identity |

**Improvements over MicroPython story (called out in #53):** first flash and update flash are the **same path** (image write). No UF2 for C; no separate "runtime once then app files" split.

**Operator gates unchanged:** confirm-board then confirm-deploy; default **no** on write. Plan text must say "This will OVERWRITE the entire application image," not "copy these five .py files."

**Prune / verify-import:** MicroPython-only. C deploy refuses or no-ops those flags with a clear message.

**Host dependency:** ESP-IDF install is machine prerequisite for C GCUs (Phase A extension): `IDF_PATH` or `idf.py` on PATH. `silico doctor` reports ready vs needs install; agent does not pretend pip can install the full IDF.

### 4.5 Gate (C)

Replace "import deploy-set under CPython" with:

1. **Host build + test:** run `[host].gate` (default for plate: configure+build+ctest under `host/`).
2. **Include hygiene:** scan `.c`/`.h` under product sources (exclude `firmware/` board backends named in allowlist). Fail if non-allowlisted units include freertos, `driver/`, `esp_`, `hal/`, `soc/`, `esp32/`, etc. (exact denylist shipped as a table; extendable in toml later).
3. Optional v1.1: compile host library with `-Werror` / pedantic flags as part of gate.

`silico gate` remains the single verb; backend chooses checker.

### 4.6 Product path (C)

Shipped defaults live in **one** C table (header or `.c` with `const` structs — xuss-c already has config defaults in protocol/config). Host tests must reference that table unmodified in at least one scenario.

Implementation sketch:

- `[host].product_defaults` points at the defaults file.
- Scanner looks under `host/` test sources for `#include` of that header, or symbol references to known default identifiers, or a conventional `product_path` test file that includes the real defaults.
- Fail if zero host tests touch the shipped table (same honesty rule as Python AST gate).

Do **not** require Python pytest for a pure C GCU. CTest is enough when `language = c`.

### 4.7 Plate `plates/gcu-c`

Minimal extractable skeleton (hello-metal, not Xuss domain):

```text
plates/gcu-c/
  AGENTS.md                 # short; points at silico + language=c
  silico.toml               # language=c, idf-flash, host gate, identity
  include/gcu/
    version.h
    hal.h                   # contract, no device headers
    defaults.h              # shipped parameter table
  src/
    version.c
    defaults.c
    domain_stub.c           # portable tick/identity helpers
  host/
    CMakeLists.txt
    test_defaults.c         # product-path: uses shipped defaults unmodified
    test_hal_double.c
  firmware/                 # ESP-IDF project
    CMakeLists.txt
    main/
      main.c                # boot: identity line, then app
      hal_board.c           # only TU that may include device headers
  install/README.md         # Day-2 one-liner (idf path via silico deploy)
```

Scaffold API:

```text
silico scaffold . --plate gcu-c
# or: silico scaffold . --runtime c
```

Existing `silico scaffold .` continues to mean `plates/gcu` (MicroPython). Protected names (`README.md`, `spec.md`, LICENSE) unchanged.

### 4.8 Protocol / escape hatch

Silico does **not** own the ASCII protocol implementation. Products (xuss-c included) must:

- Emit identity first on boot.
- Implement `repl` / `reboot` (or agreed synonyms) so agents can reclaim the port without a hard reset when possible.
- Bound serial both directions (product rails).

Silico host tools only need to **speak enough** of that contract for inspect/verify (`identity` line + optional single-line commands). Deeper protocol tests stay in the GCU's host CTest suite.

---

## 5. Work packages (implementation order)

### Phase 0 — Prerequisites on the ESP serial path (#57)

**Owner:** silico metal spine.  
**Done when:** M5GO-class board can be discovered without false CH340-only despair; BEDSIDE has esptool first-flash next to UF2; pull/inspect do not lie on modern MicroPython ESP images.

This phase is **not** the C backend, but C Day 1 metal proof reuses the same port scoring and esptool literacy.

Checklist:

- [ ] CH9102 / M5 scoring in `ports.py` + tests (`tests/test_ports.py`)
- [ ] BEDSIDE + AGENTS: ESP32 first-flash subsection (esptool erase/write; chip variants)
- [ ] pull/ls robustness as needed for ESP boots
- [ ] mpy pin honesty for old UIFlow images (do not apply wrong pin)

### Phase 1 — Config + runtime dispatcher (host-only, no board)

**Done when:** unit tests select mpy vs c backend from toml; unknown pairs fail with plain language.

- [ ] Extend `config_toml.py` readers
- [ ] Add `runtime.py` resolution
- [ ] Default language = micropython when absent
- [ ] Tests: fixture repos under `tests/fixtures/gcu_mpy/` and `tests/fixtures/gcu_c/`

### Phase 2 — C host gate + product-path + hygiene

**Done when:** `silico gate` and `silico product-path` against a **fixture** that mirrors xuss-c's host layout exit 0; deliberate violations fail.

- [ ] Run `[host].gate` subprocess for `language=c`
- [ ] Device-header allowlist scanner + tests
- [ ] Product-path scanner for C defaults + tests
- [ ] `silico doctor` lines: IDF present?, language, gate command, chip

No hardware required.

### Phase 3 — Inspect identity over serial (C)

**Done when:** with a mock serial or recorded identity stream, inspect reports match/mismatch vs `[product]`; mpy path still works.

- [ ] Serial open + identity parse shared helper (used by inspect + deploy verify)
- [ ] Branch in `inspect_device.py`; refuse `--apply-mpy-pin` when language=c
- [ ] Optional: `expect_name` / `expect_version` already on deploy — unify parsers

### Phase 4 — Deploy via IDF / esptool

**Done when:** dry plan prints build+flash recipe without writing; `--yes` invokes tools when present; missing IDF fails closed with install pointer; flags that only make sense for mpy are rejected.

- [ ] Extract mpy deploy to keep risk low
- [ ] `deploy_idf.py`: plan, build, flash, re-enumerate, verify identity
- [ ] Operator-facing plan copy ("overwrite application image")
- [ ] Integration test: mock subprocess (do not require real IDF in CI if not installed — skip or container later)
- [ ] Document Windows/macOS PATH expectations briefly in plate `install/` / AGENTS

### Phase 5 — Plate `gcu-c` + scaffold

**Done when:** `silico scaffold /tmp/hello-c --plate gcu-c` yields host gate green on a machine with a C compiler; IDF project configures on a machine with IDF (CI may test host half only).

- [ ] Author plate tree
- [ ] Scaffold flag + tests (`test_scaffold_and_cli.py`)
- [ ] Hello-metal main: identity + blink or serial-only heartbeat
- [ ] Package data includes plate in wheel/sdist

### Phase 6 — First consumer: xuss-c Day 1 on silico

**Done when:** checklist in §6 is green on real M5GO hardware for xuss-c (or honest partial with open follow-ups).

Work primarily **in tig/xuss-c**, consuming a silico pin (editable install or tag):

- [ ] Add `silico.toml` (`language=c`, chip=esp32, project=firmware, identity XUSSC)
- [ ] Complete ESP-IDF `firmware/` project (still product code; silico only deploys it)
- [ ] Wire host gate string to existing CMake/CTest
- [ ] Ensure boot identity line matches silico product keys
- [ ] Escape hatch present (spec L1)
- [ ] Pin `tig-silico` in docs/requirements once tag cuts
- [ ] Record ambiguity log in PRs; do not invent a parallel host spine

**Silico-side acceptance for this phase:** issues/PR notes that xuss-c is the proof; fix spine bugs found on the bench (Make it better than you found it).

### Phase 7 — Docs, doctrine, and Grady S3 readiness

- [ ] AGENTS.md: C plate, IDF prerequisites, deploy path; keep MicroPython default path primary
- [ ] BEDSIDE.md: esptool image flash as scary surface; after-flash re-enumerate
- [ ] lexicon: "C plate" / "runtime backend" short entries if needed
- [ ] silicov1.md: note ESP-IDF backend as forced by real GCU (xuss-c / Quilan-class), not abstract multi-runtime
- [ ] Cross-link #53, #57; close #53 only when §6 done-when is met
- [ ] S3 chip variant: same deploy verb, different `chip` / idf target — document once proven on S3 or leave open issue if only classic ESP32 was proven

### Phase 8 — Measurement rig (out of critical path for "C backend exists")

Per #53: power measurement on real hardware settles language choice for solar GCUs. Current sensing belongs to the bench story (Xuss day job / AMeter), not to silico core. Track separately; do not block Phases 1–6.

---

## 6. Done when (issue #53 acceptance)

A C hello-metal (or xuss-c) GCU on **ESP32-class** hardware passes the full Day 1 path with silico:

| Check | Proof |
|-------|--------|
| `silico doctor` | Reports language=c, IDF/chip status, ports without Python-only lies |
| `silico wait-device` | Preferred/explicit ESP port appears |
| `silico inspect --port COMx` | Identity verified against `[product]` (no mpremote REPL required) |
| Operator gates | confirm-board + confirm-deploy still required |
| `silico deploy --port COMx` | Dry plan shows IDF build + flash |
| `silico deploy --port COMx --yes --verify` | Image written; identity/version matches host |
| `silico gate` | Host-compiled tests green (CTest) |
| `silico product-path` | At least one host test drives shipped defaults unmodified |
| Escape hatch | Product `repl`/`reboot` works (product acceptance; silico redeploy without hands when possible) |
| Plate | `plates/gcu-c` scaffoldable; xuss-c is first real consumer, not the only forever template |

**Same operator experience, different toolchain.** Closing #53 without xuss-c (or plate hello-metal) on a real board is not done.

---

## 7. Testing strategy (silico repo)

| Layer | What |
|-------|------|
| Unit | toml parsing, runtime resolution, identity line parser, include hygiene fixtures, product-path C fixtures |
| CLI | scaffold `--plate gcu-c`; gate/product-path on fixture trees; deploy plan text without hardware |
| Optional metal | Manual or labeled CI job with IDF + board; not required for every PR |
| Regression | All existing mpy tests stay green; no behavior change when language omitted |

CI on silico: **must not** require ESP-IDF for the default job. Host-only C compiler (for compiling plate host tests in a fixture) is desirable when available; otherwise skip with explicit marker.

---

## 8. xuss-c integration notes (first test case)

### 8.1 What to reuse as-is

- `include/xuss/*` + `src/*` as the portable domain and protocol.
- `host/CMakeLists.txt` + CTest as `[host].gate`.
- Product identity macros (`XUSS_FW_NAME` / `XUSS_FW_VERSION`) — align string form with silico's identity parser.
- Spec rails: dead-man, escape hatch, serial bounds (product-owned).

### 8.2 What xuss-c must add for silico Day 1

1. Full IDF project under `firmware/` (their README already sketches it).
2. `silico.toml` as above.
3. Boot path: identity line **before** boot riff audio (spec already requires this).
4. Optional pin of silico for agents: docs pointing at `silico deploy` instead of raw `idf.py flash` once Phase 4 lands.
5. Host test that **must** include shipped defaults (product-path honesty) if not already guaranteed by existing tests.

### 8.3 What stays out of silico

- ESP32-Synth investigation and voice path (xuss-c spec 3.1).
- Face, PIR, ANGLE, tach routing domain.
- L2 fixture role vs Zakalwe (product / bench runner).

### 8.4 Twin discipline

Xuss (MicroPython) and Xuss-C share **acceptance rows**, not firmware trees. Silico must not force them to share `firmware/*.py`. Shared spine is verbs + identity + deploy/verify manners only.

---

## 9. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| IDF install is heavy; agents dump walls of install steps | doctor detects; one `bedside step` for "install ESP-IDF per Espressif getting started"; link official docs; do not re-host full install manual |
| Port re-enumerates after flash; COM changes | deploy verify re-runs wait/list; never reuse stale COM without re-discover (BEDSIDE) |
| Identity grammar drifts between GCU products | single parser; plate documents the line format; tests lock examples |
| C hygiene false positives on third_party | scan only product `src/` + `include/` + non-allowlisted firmware TUs; allowlist board files |
| Scope creep into Arduino/PlatformIO | refuse in review; one toolchain in toml enum |
| Closing #53 on fixtures alone | §6 requires real board for metal rows |
| Grady S3 vs M5GO classic ESP32 differences | chip/target in toml; prove classic first; open S3 checklist item if needed |
| Product-path scanner too weak (comments pass) | require include or symbol use, same spirit as Python AST gate |

---

## 10. Suggested PR breakdown (silico)

Small, reviewable steps (order aligns with phases):

1. **PR-A:** #57 port scoring + BEDSIDE esptool notes (can merge independently).  
2. **PR-B:** `runtime` + toml fields + dispatcher stubs + fixtures (no behavior change for default GCUs).  
3. **PR-C:** C gate + product-path + hygiene scanners + doctor lines.  
4. **PR-D:** Serial identity inspect + shared verify helper.  
5. **PR-E:** IDF deploy plan/flash + extract mpy deploy.  
6. **PR-F:** `plates/gcu-c` + scaffold flag + package data.  
7. **PR-G:** AGENTS/BEDSIDE/lexicon/silicov1 pointers; link xuss-c proof.  

Consumer work: **PRs on tig/xuss-c** after PR-E/F are usable via editable silico pin.

---

## 11. Sequencing summary

```text
#57 ESP serial / esptool literacy
        │
        ▼
Config + gate/product-path (host fixtures)
        │
        ▼
Inspect identity (serial) + deploy idf-flash
        │
        ▼
plates/gcu-c scaffold
        │
        ▼
tig/xuss-c consumes pin → real M5GO Day 1
        │
        ▼
Docs + close #53; S3 pin as follow-up if unproven
        │
        ▼
(optional) power measurement rig → language decision for solar GCUs
```

**Recommendation stays:** Grady ships MicroPython first on ESP32-class when #57 is honest; C backend exists so measurement-driven swap is a backend change, not a product rewrite.

---

## 12. Open decisions (resolve during implementation, log in PRs)

1. **Exact identity line grammar** — freeze one line format for plate + xuss-c (prefer key=value tokens already used by products).  
2. **IDF pin policy** — pin exact Espressif release in plate toml vs "minimum major"; prefer exact pin for reproducibility.  
3. **Build invocation** — always `idf.py -C firmware build flash` vs cmake+esptool direct; prefer `idf.py` for one documented path.  
4. **Whether `silico flash` exists** as a synonym for first-image write vs only `deploy` for C (lean: **deploy only**, plan text covers first and update).  
5. **Baud and USB-JTAG** — S3 native USB vs UART bridge; document per board in product silico.toml, not hard-coded forever to 115200-only without override.  
6. **CI IDF** — none in default silico CI until cost is justified; xuss-c may add its own IDF workflow later.

---

## 13. References

- Issue: https://github.com/tig/silico/issues/53  
- First consumer: https://github.com/tig/xuss-c  
- Twin product (MicroPython): https://github.com/tig/xuss  
- ESP MicroPython Day 1 gaps: https://github.com/tig/silico/issues/57  
- Xuss product issue: https://github.com/tig/silico/issues/50  
- Doctrine: [silicov1.md](./silicov1.md), [tenets.md](./tenets.md), [lexicon.md](./lexicon.md)  
- Operator manners: root `AGENTS.md`, `BEDSIDE.md`, vendored bedside contract
