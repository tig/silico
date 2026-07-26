# CI: host always, metal later (self-hosted)

**Issue:** [tig/silico#101](https://github.com/tig/silico/issues/101).  
**Horizon:** optional self-hosted metal CI is beta-class ([silicov1](../../specs/silicov1.md)); host CI is **always** first ship / every GCU.

Open this file when wiring Actions, claiming “CI green,” or designing practice-GCU / session-branch workflows. Do **not** load for ordinary firmware domain work.

## Two planes

| Plane | Runner | When | Green means |
|-------|--------|------|-------------|
| **Host** | `ubuntu-latest` (GitHub-hosted) | **Every** push and PR (all branches), plus `workflow_dispatch` | Plate hygiene, sim, product-path, host tests / cmake host_test / `silico gate` |
| **Metal** | Self-hosted, labeled (e.g. `self-hosted`, `silico-metal`, board class) | **Opt-in** after host green: session/lab branches, dispatch, nightly — not the default merge bar | Board talks, flash **this** SHA, identity / version match, machine-checkable accept probes |

```text
Cloud host-gate  =  always-on spine proof
Self-hosted metal =  optional bench proof (never implied by host alone)
```

**Hard rule:** host red → do not run metal. Host green alone → claim **host**, not **metal-accepted**.  
Layered DoD stays in root [AGENTS.md](../../AGENTS.md): deployed ≠ product face; CI green alone ≠ metal claim.

## Host always (shipped)

Plate workflows (`silico/plates/gcu` and `gcu-c` `.github/workflows/ci.yml`) and the silico package workflow:

1. **Trigger on all branch pushes** — not only `main` / `master` / `develop`.
2. **`pull_request`** — host gate on PRs.
3. **`workflow_dispatch`** — re-run host (and later metal) without a dummy commit.

Why: practice / evaluation work should land on **lab branches** (`session/*`, feature branches) and still get honest host CI **without** forcing firmware onto public `main` (template face). That is the #101 dual-surface prep: pristine `main` vs harness runway.

### What agents claim

| Check name / job | Allowed claim |
|------------------|---------------|
| `host-gate` green | Host layer (tests / gate / product-path as configured) |
| No metal job / metal skipped | **Not** “on the metal”; **not** Stage E metal closed |
| Future `metal-bench` green | Only the layers that job prints (deployed / metal-io / instrumented face) — never silent upgrade to human product-face accept |

## Metal later (prep, not required for this doc’s host changes)

Self-hosted ESP32 (or other) on a runner is a **bench**, not a general build farm.

### Runner shape

- Labels: e.g. `[self-hosted, silico-metal, esp32]` or board-specific (`m5go`).
- One physical board → **concurrency group** so two jobs never flash the same port.
- Tools: same as human host path (`silico`, esptool / IDF / mpremote, Python).
- Non-interactive only (`deploy --yes`, no TTY operator gates). Pin board identity in runner env (`SILICO_METAL_PORT`, expected USB id).
- **Never** metal on untrusted fork PRs (brick + secret risk). Prefer same-repo `session/*`, `workflow_dispatch`, or owner branches.

### Metal job ladder (when enabled)

1. `wait-device` / fixed port  
2. `inspect` (REPL or C identity knock)  
3. Optional recover once (first-flash / stock) if not talkative  
4. `deploy --yes --verify` (+ reset) for **this** commit → **deployed**  
5. App running (not parked forever in raw REPL)  
6. Machine accept suite (probes below)  
7. Tear down / release lock; park stock or last-known-good on failure  

### Enabling the stub

Plate `ci.yml` may include a `metal-bench` job gated by repository variable:

```text
SILICO_METAL_CI=true
```

Until steps are wired, that job is a **documented stub** (fails closed with a pointer here, or stays disabled when the var is unset — default).

### Acceptance layers (spec / suite)

| Class | CI? | Example |
|-------|-----|---------|
| Host / sim | Yes (host plane) | Product-path on shipped defaults |
| Deployed | Metal plane | `fw_name` / `fw_version` match commit |
| Metal I/O | Metal plane | Pin/telem/UART knock |
| Product face (instrumented) | Metal plane if harness exists | Mic energy, camera ROI, device `face_status` |
| Product face (human eyes/ears) | **No** by default | “Side LEDs chase”; “boot riff ~15s” — Stage D1 / field |

Prefer cheap **device self-report** knocks (`face_status`, identity) over brittle vision first. Human see/hear remains first-class for first ship; CI must not claim it without instruments.

Eyes/ears **bench observer** hardware (separate DUT-facing camera/mic board hung off the same runner) is a follow-on product spike — [tig/silico#102](https://github.com/tig/silico/issues/102), not host-CI scope.

## Practice GCUs (`xuss` / `xuss-c` / `xuss-lame`)

| Surface | Role |
|---------|------|
| `main` | Prefer **product-only clean start** (public template). |
| Lab / `session/*` | Harness runway; host CI must still run (host always). |
| `tags/clean-start`, `attempt-*` | Baseline + archives (see #101). |

Do **not** require “push firmware to main so Actions runs.” Host always removes that excuse. Full prepare/archive/restore-main CLI is #101 follow-on; this knowledge is the CI contract those tools will assume.

## Anti-patterns

- Host-only green narrated as “CI proves metal” or “Stage E done.”  
- Main-only `on.push.branches` so lab branches never get host gate.  
- Metal job on every fork PR.  
- Two concurrent metal jobs on one USB board.  
- Claiming product-face accept from version string alone.  
- Skipping host plane because “we have a board on the desk.”

## Related

- Root [AGENTS.md](../../AGENTS.md) — layered DoD, Stage E, practice GCU clean start  
- [first-flash.md](first-flash.md), [esp32-usb-serial.md](esp32-usb-serial.md) — prep / duplex when metal is wired  
- Plate workflows: `silico/plates/gcu/.github/workflows/ci.yml`, `gcu-c` twin  
