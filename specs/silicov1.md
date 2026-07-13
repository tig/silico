# silico v1

**Status:** Draft spec for build.
**Steward:** Tig Kindel (github.com/tig/silico). Not a company product line.
**Scope:** The spine required by three Pi-class GCUs (RP2040 / MicroPython first).
**Non-scope:** Industry default. Category marketing. Cloud fleet. Built-in phone-home for all GCUs. Arduino-class plates as a deliverable. Company branding of the spine. Full v2 narrative (longer-term vision lives in [wb-2026-fall-three-gcus.md](./wb-2026-fall-three-gcus.md) FAQ 40).

Related: [tenets.md](./tenets.md), [gcu-codenames.md](./gcu-codenames.md), [wb-2026-fall-three-gcus.md](./wb-2026-fall-three-gcus.md).

## 0. Why this exists

We work backwards from the Grady experience ([v1 WB](./wb-2026-fall-three-gcus.md)):

> With just Claude Code on my Mac, I had the device working end-to-end the next day, and in a potential customer's hand the day after that. Silico is now a foundational piece of our company's technology.

Silico tenets: [tenets.md](./tenets.md) (unless you know better ones).

Skin in the game:

1. **Device ops at scale** (Media Center, Home Server, Phone, Echo, Control4).
2. **Lived agent path:** Zakalwe firmware **100% agents**; detailed spec from a rough brief; steward is not Pi or EE expert. Judgment and host-first done are human.

If v1 only works when a career embedded engineer authors the code, or only when Tig is in the room, we failed the sentence above.

## 1. Purpose of v1

Make the two-day path real and repeatable for three GCUs ([gcu-codenames.md](./gcu-codenames.md)):

1. **Zakalwe** (closed-loop control). First extraction; agent-authored firmware existence proof.
2. **Quilan** (slow field logger). Grady's GCU; only starter that needs WAN phone-home in the *app*.
3. **Sma** (sleep-friendly mesh node). Local mesh is product IP.

v1 succeeds when:

1. **Day 1:** non-software human + agent on a Mac → real USB device (+ sim) end-to-end, host gate green.
2. **Day 2 (alpha):** same verified build can leave as a **prototype** with a **real customer for alpha** feedback — not beta polish; not full integrity suite.
3. **~1 month later (beta horizon):** more customers can get beta-class units; **update integrity** (definition TBD — [spike](https://github.com/tig/silico/issues/4)) and optional self-hosted metal CI belong here, not on Day 2.
4. Ongoing: silico remains how that company updates edge (foundational, not a demo).
5. All three GCUs share the spine without private folklore dumps into silico.

> **Host-first** means done lives on the host (tests, compile gates, sim or scenario gates) before anyone treats a flash as proof. That is how a non-expert prompts an agent without lying.

> **Gobbledygook** means port discovery, multi-COM hazards, deploy file sets, version verify, recovery, anti-patterns, and CI that means metal.

## 2. Principles (build rules under the tenets)

1. Private domain logic never becomes a silico feature to win a demo (**Apps stay apps**).
2. Promote to silico only when a second GCU needs the same thing (**Extract, then open**).
3. No hardware at import time. Init constructs the world.
4. I/O and time cross a HAL as boring values (ints, floats, bools), not driver objects.
5. Install and update verify version identity. Mismatch is failure (**Prompt for metal**, **Host first**).
6. Agents author firmware and detailed specs by default. Chat folklore is not a release artifact (**Agents write the code**).
7. Agents run host setup, CI, deploy, and first-flash guidance; help the operator; do not assume ops literacy (**Agents operate the host path**).
8. Agent friction becomes silico doc/infra fixes or issues on `tig/silico`, not chat-only recovery (**Make it better than you found it**).
9. CI has no serial port. Hardware harness is optional and local (**Host first**).
10. Do not claim external proof when only extraction is proven (**Extract, then open**).
11. Do not require the human steward to be the MCU, electrical, or DevOps expert to merge.

## 3. The three GCUs (v1 forcing function)

v1 is not abstract. Distinct shapes force a spine that is not one product's costume.

### 3.1 Zakalwe (control loop)

1. Fast periodic control (order of tens of Hz).
2. Closed-loop plant on host for regression.
3. USB telemetry while running.
4. Customer update over USB serial today; first runtime flash may still be UF2 drag.
5. No product need for internet or phone-home. Local host USB is enough.
6. **Origin constraint:** agent-authored application firmware and agent-authored detailed spec from a rough human/partner brief are first-class. The spine must support that workflow, not a "expert types MicroPython" workflow.

### 3.2 Quilan (slow field logger)

1. Slow sample and store periods (seconds to minutes), not a 50 Hz religion.
2. Power and enclosure reality matter more than a single control law.
3. Plant is environment and sensors, not a one-off physics toy.
4. Same install/verify and host-gate doctrine as Zakalwe.
5. **Only starter GCU that truly needs internet and phone-home.** Real for the *app*. Not a silico v1 spine requirement (section 14).

### 3.3 Sma (sleep and radio)

1. Wake cycles and sleep. "Tick" means period of work, not a fixed high-rate control period.
2. Battery budget is part of the product story.
3. Mesh stack is product IP. silico does not own the mesh protocol in v1.
4. Bring-up still needs USB host path and version verify.
5. Local mesh is not WAN phone-home. No silico v1 requirement for WAN or cloud.

If a design helps only Zakalwe and harms the other two, it is not v1 spine. It is Zakalwe.

If a design is "built-in internet and phone-home for every GCU via silico," it is not v1. Quilan may implement uplink in the app. The spine catches up later (section 14.1).

## 4. Customers of v1

1. **GCU authors** (start with Tig; partners who supply rough domain briefs): plates, deploy tools, gates, docs. Need not be MCU experts.
2. **Agents editing GCU repos:** AGENTS.md, anti-patterns, commands that mean done. Default authors of firmware and detailed specs.
3. **End customers of GCUs:** install/update without knowing silico exists.

Target after v1: vertical teams (Grady-shaped) who **Prompt for metal** and will not staff a device-ops priesthood.

## 5. Repository shape (spine)

Public repo contains:

1. **Docs and doctrine** (this spec, v1 WB, tenets, codenames).
2. **Host library** for deploy, version parse, port scoring, shared test helpers.
3. **Product plate** (template) for a GCU repo layout.
4. **One thin public example GCU** (not Zakalwe domain) green in CI.
5. **CI** for the spine itself.

Private GCU repos pin silico as a **host** dependency and follow the plate. Device `firmware/` never imports silico. Full Day 1 checklist (Grady or anyone discovering this repo): [v1 WB FAQ 4](./wb-2026-fall-three-gcus.md).

```text
# GCU depends on silico (host / CI only)
requirements-dev.txt:
  silico @ git+https://github.com/tig/silico.git@<tag>
  # or while extracting:  -e /path/to/tig/silico

firmware/   -> board
silico      -> Mac / CI only
```

The GCU needs a GitHub remote (or equivalent) so CI can run the host gate. A package pin alone is necessary but not sufficient for Grady's path.

### 5.1 GCU repo layout (plate)

```
<gcu>/
  AGENTS.md
  CLAUDE.md                 # pointer to AGENTS.md
  firmware/                 # on-device application (agent-authored by default)
  sim/                      # product plant + tests; never deployed
  scripts/                  # thin wrappers: call silico host APIs
  install/                  # end-customer install and update docs
  dev/                      # process notes (CI/CD), not customer docs
  requirements-dev.txt      # pins silico @ tag/SHA + pytest; mpy-cross == device runtime
  pytest.ini
  .github/workflows/ci.yml
  silico.toml               # product config for silico host tools
```

## 6. Firmware architecture (device)

### 6.1 Required modules (conceptual)

1. `version` with `FW_NAME` and semver `FW_VERSION`.
2. `hal` contract that imports nothing on the device path.
3. Device HAL backend (v1: RP2040 / MicroPython).
4. `main` with `init(hal=None)` and periodic `tick` (or explicit run period).
5. Domain modules owned by the GCU (private). Agents write them under contracts.
6. On-device harness or self-test entry that is not an infinite boot loop.

### 6.2 Rules

1. Domain policy modules do not import `machine`.
2. `main` does not construct hardware at import. Function-local import of device HAL is fine.
3. IRQ handlers use fixed buffers only.
4. One owner of status outputs per tick.
5. Single loop or schedule; no nested infinite mode runners calling each other.

### 6.3 HAL surface

v1 does **not** define product-specific pin or actuator methods as silico API.

v1 defines:

1. Time: ticks, tick diff, sleep.
2. Pattern for product-specific read/write methods.
3. Host sim backend implementing the same product HAL for tests.
4. Hygiene tests: `hal` imports nothing; device backend implements the contract; machine import allowlist is config.

## 7. Host gate

Every GCU CI and every honest "firmware done" includes:

1. Unit and packaging tests on host.
2. Bytecode or compile gate for on-device sources (`mpy-cross` **pinned to the device MicroPython version**, not a loose floor).
3. Hygiene gates (import rules, core file set, no sim in deploy set).
4. At least one scenario or smoke exercising init and tick against a plant or fake HAL.
5. Print or log of `FW_NAME` and `FW_VERSION` under test.

No COM port in CI.

### 7.1 Definition of done (agents and humans)

A change to `firmware/` is done only when the GCU's named host command is green. Flashing is optional confirmation.

This is the minimum **Prompt for metal** / **Host first** bar. Soften it and a non-expert cannot trust agent-authored firmware. Soften it and Grady is right to walk away.

## 8. Install and update (customer path)

### 8.1 Lifecycle

1. **Discover** board (VID/PID scoring; explicit port wins; never blind auto on multi-device hosts).
2. **Bootstrap** host tools if needed (Python **3.11+**, mpremote).
3. **Runtime** (once): document UF2 or equivalent first flash of MicroPython.
4. **Application:** deploy configured core file set in dependency order.
5. **Verify:** device `FW_VERSION` matches host.
6. **Optional harness:** known success signature.

### 8.2 Maturity for v1

1. **Required:** scriptable path from a product checkout.
2. **Target:** release zip per GCU (no git required).
3. **Not required for Day 1–2:** MSI/GUI installer, OTA, full signing PKI, fleet CD with automatic rollback (FAQ 40).
4. **Not required for Day 2 alpha:** update integrity protection beyond version identity — see month-later beta horizon and integrity spike.
5. **Open (spike):** what "protecting integrity" means for beta units (hash manifest, signing, provenance, CRA hooks, …).

### 8.3 Port scoring (v1 defaults)

Prefer Raspberry Pi / MicroPython USB (`2e8a`). Demote CH340 (`1a86`) and Debug Probe (`2e8a:000c`). Always allow `--port`.

## 9. Version identity

1. Semver in device `version` module is source of truth for the app build.
2. Host reads the same file before deploy.
3. After deploy, host queries device; noise-tolerant `FW_VERSION=` (or successor).
4. Mismatch fails the update.

## 10. Agent contracts

Each GCU ships:

1. `AGENTS.md` with stack, layout, done command, interface map, priorities, What Not To Do.
2. Anti-pattern notes for known model failures.
3. Pointer stubs (`CLAUDE.md` and kin) to the canonical agent doc.

silico ships the template and common sections. Product fills domain (from rough human briefs; agents detail and implement).

See [Building For The Robots](https://blog.kindel.com/2026/05/26/building-for-the-robots/). v1 requires "done" is a command, not a vibe. Without this, agent-authored firmware is gambling.

## 11. CI/CD doctrine

1. Validate branch and ship branch named once per repo and written down.
2. Every PR and push to those branches runs the host gate.
3. Release is green ship branch plus tag matching `FW_VERSION` for GCU releases.
4. Dependabot (or equivalent) on host tools encouraged.
5. Branch protection may be process-only on private free plans. Document that.

Spine CI tests silico. GCU CI tests the product. No hardware in CI.

## 12. Config surface (per GCU)

Machine-readable config declares at least:

1. Product name (may be codename in public).
2. Firmware directory.
3. Core deploy file list (ordered).
4. Extra deploy files (harness, scope tools).
5. Machine import allowlist.
6. USB prefer / avoid hints.
7. Platform probe expectation (for example `rp2`).

## 13. Extraction order (implementation)

1. Doctrine: tenets, v1 WB, this spec, codenames.
2. Extract deploy, semver parse, port scoring from Zakalwe into a host library.
3. Extract parameterized hygiene helpers.
4. Plate + thin example green in CI and agent-operable from AGENTS.md.
5. Point Zakalwe at the library without regressions (agent path remains default).
6. Generate Quilan and Sma repos from the plate when those apps start.
7. Only then add targets, phone-home spine features, or install polish a second GCU demanded.

## 14. Non-goals (v1)

1. Arduino / PlatformIO plate as a deliverable.
2. Built-in internet, phone-home, cloud accounts, fleet dashboards, or remote OTA as silico spine features. Quilan may phone home in app code.
3. Replacing MicroPython with C as the default.
4. Shipping private product source in silico.
5. Claiming platform status, company org chart, or external proof.
6. Perfect multi-os desktop GUI installers.
7. Features for imaginary unicorns before three GCUs force the shape.
8. Requiring human hand-authorship of firmware as the blessed path.

### 14.1 Later (not v1; see also v1 WB FAQ 40)

1. Phone-home through silico when a second GCU needs Quilan's app loop; USB remains always available.
2. Multi-target plates when a GCU forces them.
3. Echo-shaped continuous deploy with automatic rollback for fleets, only after host-first is boring.
4. External default among vertical teams.

Until then, Quilan owns modem, credentials, and uplink protocol in private app code.

## 15. Open decisions

**Closed**

1. **License: Apache-2.0** (patent grant for serious vertical legal review).
2. **Python floor: 3.11+** (do not guide operators onto EOL 3.9).
3. **Pin silico by tag or commit SHA**, not `@main` (version identity).
4. **mpy-cross** pinned to device MicroPython runtime (single source in `silico.toml` when tooling lands).

**Still open**

1. Package name on PyPI vs git URL pin only for early v1 (git pin is enough until publish).
2. Exact config file name (`silico.toml` vs tool table in pyproject).
3. Ship branch name for silico itself.
4. How much of Zakalwe's sim plant pattern is example vs library.
5. Field definition per GCU for the Fall 2026 WB.
6. When phone-home graduates from Quilan app code into silico.
7. What "shout from the rooftops" means as external proof.
8. Minimal package layout so `pip install` of a tag works (make-PR-true; pre-alpha until then).
9. CLI verbs (spec now; see tui-cs/cli design discussion) and Day 1 rehearsal harness.
10. MicroPython host-sim stack ([issue #3](https://github.com/tig/silico/issues/3)); integrity for beta ([issue #4](https://github.com/tig/silico/issues/4)).

## 16. Acceptance for silico v1

Primary (the sentence we work backwards from):

1. A Grady-shaped path is documented and runnable: Claude Code (or equivalent) on a Mac → device end-to-end in about a day with host gate green.
2. The same path supports putting that unit with a potential customer the next day (install/verify, not heroics).
3. After the demo week, silico is still the update/prove path (foundational).

Supporting:

4. Spine CI green; thin public example GCU deployable with version verify.
5. Zakalwe on the host library; agent-authored path remains default.
6. Quilan and Sma plates exist with host gate green (domain may be stubbed).
7. AGENTS.md names the done command; flash is confirmation only.
8. Docs distinguish "Tig can do it" from "stranger can do it without Tig."

Until then, call it draft.
