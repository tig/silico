# Plan: ESP32 C / ESP-IDF backend (#53)

Tracks [tig/silico#53](https://github.com/tig/silico/issues/53). First consumer: [tig/xuss-c](https://github.com/tig/xuss-c). Related: [#57](https://github.com/tig/silico/issues/57), [#50](https://github.com/tig/silico/issues/50), [silicov1.md](./silicov1.md), `AGENTS.md`, `BEDSIDE.md`.

## Why I am writing this

Grady read the PRFAQ, leaned in, and asked whether silico can do both C and MicroPython. His board is ESP32-S3, not Pi class. His reason was power: solar, battery, language as a knob.

I do not buy the power argument yet. Sleep current dominates a duty-cycled device. Language only owns the awake milliseconds. Get it working first. Measure. Then argue.

That advice is dishonest if switching languages is a rewrite. So I want the C door open against the same contracts and the same spine. Customer zero's board is ESP32 either way.

> **A backend** is the plumbing that puts a GCU on the metal. The contracts (identity, protocol, host-first gate, product-path honesty, operator gates) stay language-agnostic. Only the tools change.

A C GCU that prints its identity line and answers the protocol is indistinguishable from a Python one at the port. That is the design working as intended.

## What I mean by "C"

ESP-IDF is fine with modern C++. Naming this backend **C** (xuss-c, `language = c`, `plates/gcu-c`) is a product and spine choice, not a claim that the chip is C-only.

I want host L0 domain in **portable C** behind a HAL seam (`cmake` + `ctest`, no IDF, no Arduino). Metal is **ESP-IDF**. Prefer C for the plate and for anything that must stay host-testable. C++ is allowed in board and driver translation units when a product needs it (`extern "C" app_main`, same identity line).

I do **not** want a third peer runtime called `language = cpp`. One non-Python backend path: ESP-IDF. Domain host-gated in C by default. C++ is a product choice inside `firmware/`, not a silico matrix row.

## Goal

Same operator path as MicroPython. Same verbs: `doctor`, `wait-device`, `inspect`, `deploy`, `gate`, `product-path`. Different toolchain underneath.

Prove it on **xuss-c** before anyone claims Grady's S3 path is "C-ready." Hello-metal on `plates/gcu-c` is a prerequisite. It is not the whole acceptance story.

## What stays out

1. Arduino core or PlatformIO as silico's official dual-runtime path. One non-Python backend: ESP-IDF for ESP32-class. Pico SDK later only if an RP2040 GCU forces it.
2. C++ as a separate silico language peer.
3. Xuss voice, edge, or face domain living in silico. That stays in `tig/xuss` and `tig/xuss-c`.
4. Claiming C is required for battery life without a measured draw on the product build.
5. Soft-forking Bedside principles into a second essay. Metal notes stay in `BEDSIDE.md`.
6. Making every GCU dual-language. Default plate stays MicroPython. C is opt-in.

Not out of scope: a GCU that uses C++ inside its ESP-IDF board backends while keeping host domain C and `language = c`.

## Fix Python-on-ESP first (#57)

#53 already sequences MicroPython-on-ESP gaps before the C backend. #57 is that track for M5GO and classic ESP32:

1. Score CH9102 (and known M5 VID/PID) honestly, not as CH340 despair.
2. Document esptool first-flash next to UF2 in BEDSIDE and AGENTS.
3. Make `silico pull` survive boot banners.
4. Pin mpy from `sys.implementation.version`, not language version lies on ancient UIFlow.

Those fixes unblock Day 1 in Python, which is still what I recommend. This plan depends on esptool being a first-class metal path. It adds build-and-flash of an IDF app image as the C deploy path.

Do not call C Day 1 "operator complete" until doctor, wait-device, and esptool notes stop lying on M5GO. Host-only C work can land on fixtures without a board. Metal proof waits on a working ESP serial path.

## What is broken today

The contracts are language-agnostic. The plumbing is not.

| Contract | Python plumbing today |
|----------|------------------------|
| Identity on the link | mpremote plus `version.py` |
| Protocol, escape hatch | product firmware (any language can speak it) |
| Host-first seam and product-path | CPython import, AST `machine` allowlist, pytest defaults scan |
| Deploy and verify | mpremote file copy; UF2 first-flash story |
| Runtime pin | `[runtime].mpy_cross` |

Scaffold knows one plate. Deploy assumes mpremote. Inspect assumes a REPL. Gate assumes Python sources. Doctor prefers RP2040 and still demotes CH9102 like a random CH340 (#57). First-flash docs still think the world is BOOT and `RPI-RP2`.

## First consumer: xuss-c

[tig/xuss-c](https://github.com/tig/xuss-c) is the designated first consumer. It is **far thinner than this plan reads if you skim the headings.** That is intentional.

Today it is **spec only** (plus AGENTS, README, and a boot-riff asset). No `src/`, no `host/` CTest suite, no IDF `firmware/` tree, no `silico.toml`. The contract lives in `spec.md`. Firmware and host gates get built from that contract by an agent, on a branch, with an ambiguity log. I am not pretending the C twin of Xuss is half-implemented so silico can claim a free ride.

What xuss-c already gives this plan:

1. A real product contract (edge engine, protocol, rails, acceptance rows) that must stay language-agnostic at the port.
2. Hardware fix: M5GO / classic ESP32 (same class as the Python twin).
3. An explicit first consumer so #53 cannot close on hello-metal alone.

What it does **not** give (yet), on purpose:

1. Portable C sources or a host CTest layout to "reuse as-is."
2. An IDF project ready for `silico deploy`.
3. A silico pin or Day 1 leave-behind.

The silico bridge in their spec is optional for product L1 by hand. This plan is still that bridge. Silico Day 1 exit for C requires it. Building domain and metal **in xuss-c** is consumer work, not evidence that the consumer already exists in code.

#53's done-when names ESP32-S3 (Grady). Xuss-C is classic ESP32 on M5GO. One backend: ESP32-class under ESP-IDF. Prove on M5GO first. Re-pin `chip` for S3 later. Do not invent a second deploy story.

## Same operator experience

The human (and the agent helping them) still:

1. Starts only after a clear go.
2. Gets host gate green.
3. Plugs a data USB cable; agent runs a long `wait-device`.
4. Runs `inspect` and verifies identity against the manifest.
5. Confirms the port is the product board, then confirms the write, then `--yes`.
6. Checks identity after flash. Escape hatch (`repl` / `reboot`) stays a product requirement.

They do not need to know whether the image was five MicroPython files or one IDF binary once the write is confirmed.

## Design rules

1. Backend, not rewrite. Runtime from `silico.toml`. Contracts stay language-agnostic.
2. Host first still means host first. Domain tests on the host. Flash confirms; it does not invent truth.
3. "C" is the spine default, not a C++ ban. See above.
4. Deploy still needs explicit `--port` and operator yes. Plan text names the flash in plain words.
5. Hygiene is the allowlist, spelled differently. Python: `machine` imports. C: device headers only in allowlisted board TUs (`.c` or `.cpp`).
6. Extract, then open. Grow the plate from what xuss-c forces, once xuss-c has real code. Do not invent a rich xuss-c tree inside this plan and call it done.
7. Do not dual-maintain product domain in silico. The plate is hello-metal and a HAL skeleton only.

## Architecture

### Runtime selection

Branch on toml. Do not guess from file extensions.

```toml
[product]
name = "Xuss-C"
fw_name = "XUSSC"
fw_version = "0.0.1"

[runtime]
language = "c"                    # "micropython" | "c"  (default: micropython)
                                  # "c" means ESP-IDF backend; not "C only forever in firmware"
toolchain = "esp-idf"             # only valid pairing for language = c in this plan
esp_idf = "v5.3.2"                # example pin; freeze when the plate ships
board = "m5stack-core-esp32"
chip = "esp32"                    # esptool: esp32 | esp32s3 | …

[host]
gate = "cmake --build build/host --target test"
product_defaults = "include/xuss/config.h"   # example shape once xuss-c has sources; not present today

[hal]
allow_device_headers = ["board_m5go", "hal_board"]

[deploy]
mode = "idf-flash"
project = "firmware"
```

Omit `language` (or set `micropython`) and every existing GCU keeps today's behavior. No silent deploy change for Python plates.

### Module map

| Piece | Job |
|-------|-----|
| `config_toml.py` | Read language, toolchain, IDF pin, chip, deploy mode, allowlists, gate string. |
| `runtime.py` (new) | Resolve backend; fail closed on unknown pairs. |
| `deploy_mpy.py` | Current mpremote path, extracted without behavior change. |
| `deploy_idf.py` (new) | Plan, build, flash via `idf.py` / esptool. |
| `deploy.py` | Thin dispatcher. |
| `inspect_device.py` | mpy REPL path or serial identity-line path. |
| host hygiene / `gate_c` | No device headers outside allowlist. |
| `product_path.py` | C defaults: compiled use of shipped table in host tests. |
| `doctor.py` | IDF on PATH, language, chip, honest ports. |
| `scaffold.py` | `silico scaffold . --plate gcu-c`. |
| `plates/gcu-c/` | Hello-metal C plate. |
| `BEDSIDE.md` / `AGENTS.md` | Point at the path; do not re-host the full IDF install manual. |

### Inspect (no REPL required)

On boot or on `identity`, the app prints one stable line:

```text
fw_name=XUSSC fw_version=0.0.1
```

One identity grammar for both backends.

For `language = c`: open the port (default 115200, toml override), knock with newline and `identity`, parse, compare to `[product]`, never write. Refuse `--apply-mpy-pin`. Pin IDF from toml for now; optional device self-report later if we need it.

After deploy, re-parse identity. Port may re-enumerate after flash. Re-discover before claiming success. BEDSIDE already says that.

### Deploy

| Step | Plan (no `--yes`) | Write (`--yes`) |
|------|-------------------|-----------------|
| Preconditions | `language=c`, project exists, port listed | same, plus operator yes |
| Build | Show the `idf.py -C <project> build` that will run | Run it; fail closed |
| Flash | Show chip, port, image / `idf.py flash` | Flash |
| Verify | Note identity check | Reset if needed; wait for port; parse identity |

First flash and update flash are the same path: image write. That is better than the MicroPython story (runtime once, then app files forever).

Operator gates unchanged. Plan text must say this will **overwrite the entire application image**, not "copy these five `.py` files."

`--prune` and `--verify-import` are MicroPython-only. Refuse them with a clear message on the C path.

ESP-IDF install is a machine prerequisite. Doctor reports ready versus needs install. Agents do not pretend `pip` installs IDF.

### Gate

1. Run `[host].gate` (configure, build, ctest under `host/`).
2. Include hygiene: fail if non-allowlisted units pull freertos, `driver/`, `esp_`, `hal/`, `soc/`, `esp32/`, and friends.
3. Optional later: pedantic host compile flags.

One verb: `silico gate`. Backend picks the checker.

### Product path

Shipped defaults live in one C table. At least one host test must drive the product path with those values unmodified.

A gate a comment or bare `#include` can pass is the same green-but-broken gate I already refuse on the Python side.

Require compiled use: include or link the shipped defaults, and pass a field or table pointer into the product path. Prefer a real identifier check. Fail if zero host scenarios run on shipped defaults. Extra scenarios may override edges; zero on shipped is a fail.

CTest is enough when `language = c`. Do not force pytest on a pure C GCU.

### Plate `plates/gcu-c`

Hello-metal only. Not Xuss domain.

```text
plates/gcu-c/
  AGENTS.md
  silico.toml
  include/gcu/          # version, hal, defaults
  src/                  # portable domain stubs
  host/                 # CMake, CTest, product-path test
  firmware/main/        # IDF: identity first; board TU only for device headers
  install/README.md
```

```text
silico scaffold . --plate gcu-c
```

Bare `silico scaffold .` still means MicroPython `plates/gcu`. Protected names unchanged: `README.md`, `spec.md`, LICENSE.

### Protocol

Silico does not own the ASCII protocol. Products must emit identity first, ship `repl` / `reboot`, and bound serial both directions. Host tools only speak enough of that contract for inspect and verify. Deeper protocol tests stay in the GCU's CTest suite.

## Work order

### Phase 0: ESP serial path (#57)

Not the C backend. C metal proof reuses it.

Done when M5GO-class boards are discoverable without false CH340-only despair, BEDSIDE has esptool next to UF2, and pull/inspect do not lie on modern MicroPython ESP images.

Checklist:

1. CH9102 / M5 scoring in `ports.py` plus tests.
2. BEDSIDE and AGENTS: ESP32 first-flash subsection.
3. Pull/ls robustness against ESP boots.
4. Honest mpy pin for old UIFlow images.

### Phase 1: Config and runtime dispatcher

Host-only. No board.

Done when unit tests select mpy versus c from toml and unknown pairs fail in plain language.

### Phase 2: C gate, product-path, hygiene

Done when `silico gate` and `silico product-path` pass on a **fixture** that looks like the host layout a C GCU will grow into (not a claim that xuss-c already has that tree), and deliberate violations fail. Doctor reports IDF, language, gate, chip.

### Phase 3: Serial identity inspect

Done when a mock or recorded stream matches or mismatches `[product]`, and the mpy path still works. Shared parser for inspect and deploy verify. Refuse `--apply-mpy-pin` when `language = c`.

### Phase 4: IDF deploy

Done when dry plan prints build and flash without writing, `--yes` runs tools when present, missing IDF fails closed, and mpy-only flags are rejected. Prefer mocked subprocess tests so default CI does not need IDF.

### Phase 5: Plate and scaffold

Done when `silico scaffold … --plate gcu-c` yields a host-green tree with a C compiler, and the IDF project configures where IDF exists. CI may test only the host half.

### Phase 6: xuss-c Day 1 (required to close #53)

Hello-metal is a prerequisite. It does not close #53.

xuss-c starts from **spec only**. This phase builds the product and wires silico; it does not "hook up" code that is already there.

Work in `tig/xuss-c` against a silico pin (editable install or tag):

1. Implement host L0 from `spec.md` (portable C, CMake, CTest, shipped defaults, product-path honesty).
2. Implement metal from `spec.md` (ESP-IDF under `firmware/`, identity first, escape hatch, rails).
3. Add `silico.toml` (`language = c`, chip, project, identity).
4. Wire `[host].gate` to the new CTest path; pin `tig-silico` when a tag exists.
5. Ambiguity log in every PR. No parallel host spine invented to avoid silico.

Fix every spine bug found on the bench. Make it better than you found it.

### Phase 7: Docs and S3 readiness

AGENTS, BEDSIDE, lexicon, silicov1 pointers. Close #53 only when Phase 6 is green on xuss-c. Document S3 as the same verb with a different `chip` once proven, or leave an open follow-up.

### Phase 8: Measurement rig (not on the critical path)

Grady is right that power is measured on real hardware or not at all. Current sensing belongs to the bench story (Xuss day job), not silico core. Track it separately. Do not block Phases 1 through 6 on it.

## Done when (#53)

Close #53 only when **xuss-c** completes Day 1 on ESP32-class hardware with silico. Hello-metal is required and not sufficient.

### Prerequisite: `plates/gcu-c`

1. Scaffold yields a buildable tree.
2. Day 1 verbs work on the plate (doctor through product-path).
3. Minimal escape hatch, or an honest metal-TODO that says so.

### Required: xuss-c

1. `doctor` reports `language = c` without Python-only lies.
2. `wait-device` finds the ESP port.
3. `inspect --port COMx` verifies identity without mpremote.
4. confirm-board and confirm-deploy still required.
5. `deploy` dry plan shows IDF build and flash.
6. `deploy --yes --verify` writes the image; identity matches host.
7. `gate` is green on xuss-c CTest.
8. `product-path` proves compiled use of shipped defaults.
9. Escape hatch works.
10. xuss-c is the consumer that validates the architecture.

Same operator experience. Different toolchain. Closing on fixtures alone is not done.

## Testing in silico

Unit tests for toml, runtime resolution, identity parser, include hygiene, product-path fixtures. CLI tests for scaffold, gate, product-path, and deploy plan text. Optional metal job later. All existing MicroPython tests stay green when language is omitted.

Default silico CI must not require ESP-IDF. Host C compiler for plate fixtures is nice when available; otherwise skip with an explicit marker.

## xuss-c notes

**Honest state:** spec-first skeleton on purpose. Do not update this plan as if host sources, IDF firmware, or CTest already exist. When those land, they land in `tig/xuss-c` PRs with an ambiguity log, not by rewriting history here into "already half done."

What the agent must still build (from `spec.md`):

1. Portable domain and protocol under something like `include/` + `src/`.
2. Host gate (`host/` + CMake + CTest) with product-path on shipped defaults.
3. ESP-IDF `firmware/` with identity before boot riff, escape hatch, rails.
4. `silico.toml` and a silico pin once deploy works.

Keep out of silico: ESP32-Synth investigation, face/PIR/ANGLE/tach domain, L2 fixture versus Zakalwe.

Xuss and Xuss-C share acceptance rows, not firmware trees. Shared spine is verbs, identity, and deploy manners only.

## Risks

1. IDF install is heavy. Doctor detects it. One bedside step points at Espressif's getting started. Do not re-host the full manual.
2. Port re-enumerates after flash. Re-discover. Never reuse a stale COM.
3. Identity grammar drifts. One parser. Plate documents the line. Tests lock examples.
4. Hygiene false positives on third_party. Scan product sources; allowlist board TUs.
5. Arduino or PlatformIO scope creep. Refuse in review.
6. `language = cpp` as a third peer. Refuse.
7. Closing #53 on hello-metal alone. Refuse.
8. Product-path scanner too weak. Require compiled use into the product path.

## PR breakdown (silico)

Small steps, same order as the phases:

1. PR-A: #57 port scoring and BEDSIDE esptool notes (can merge alone).
2. PR-B: runtime and toml fields, dispatcher stubs, fixtures.
3. PR-C: C gate, product-path, hygiene, doctor lines.
4. PR-D: serial identity inspect and shared verify helper.
5. PR-E: IDF deploy; extract mpy deploy.
6. PR-F: `plates/gcu-c` and scaffold flag.
7. PR-G: AGENTS, BEDSIDE, lexicon, silicov1; point at xuss-c proof.

Consumer work lands on `tig/xuss-c` after PR-E and PR-F are usable via an editable silico pin.

## Sequencing

```text
#57 ESP serial / esptool literacy
        |
        v
Config + gate / product-path (host fixtures)
        |
        v
Inspect identity + deploy idf-flash
        |
        v
plates/gcu-c scaffold
        |
        v
tig/xuss-c on real M5GO Day 1
        |
        v
Docs; close #53; S3 follow-up if needed
        |
        v
(optional) measure power; then argue language
```

Recommendation stays: ship MicroPython first on ESP32-class once #57 is honest. Build the C backend so a measurement-driven swap is a backend change, not a product rewrite.

## Open decisions (log in PRs)

1. Freeze one identity line format for plate and xuss-c (prefer key=value tokens products already use).
2. Pin exact IDF release in plate toml (prefer exact over "minimum major").
3. Prefer `idf.py -C firmware build flash` as the one documented path.
4. No separate `silico flash` verb for v1; `deploy` covers first image and update.
5. Baud and USB-JTAG per board in product toml, not hard-coded forever to 115200 with no override.
6. No IDF in default silico CI until cost is justified.
7. Plate hello-metal stays C; product `firmware/` may add `.cpp` board TUs without changing `language = c`.

## References

- Issue: https://github.com/tig/silico/issues/53
- First consumer: https://github.com/tig/xuss-c
- Twin (MicroPython): https://github.com/tig/xuss
- ESP Day 1 gaps: https://github.com/tig/silico/issues/57
- Xuss product: https://github.com/tig/silico/issues/50
- Doctrine: [silicov1.md](./silicov1.md), [tenets.md](./tenets.md), [lexicon.md](./lexicon.md)
- Operator path: root `AGENTS.md`, `BEDSIDE.md`, vendored bedside contract
