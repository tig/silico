# Working Backwards: Silico v1 — Three GCUs in the Field (Fall 2026)

**Stage:** First draft for broad foundational input. Ambition date is Fall 2026.
**Artifact form:** Press release plus FAQ
**Scope of this doc:** Silico **v1** only. Longer-term vision is FAQ 40, not a separate v2 narrative (yet).

How to read: we work backwards from **this** customer experience. Everything in the PR, FAQ, tenets, and v1 spec is invented only to make this true (and repeatable without Tig in the room):

> "I met Tig, and he showed me Silico. With just Claude Code on my Mac, I had the device working end-to-end the next day, and in a potential customer's hand the day after that. Silico is now a foundational piece of our company's technology."
> — Grady, CEO and Founder of Quilan

The press release is that experience made public. The FAQ is everything the PR cannot carry without becoming a strategy deck. See [tenets.md](./tenets.md).

Method notes:

- [Tenets](https://blog.kindel.com/2020/02/10/tenets/) and [Silico tenets](./tenets.md)
- [How To: Write a Working Backwards Doc](https://blog.kindel.com/2024/07/23/how-to-write-a-working-backwards-doc/)
- [A FAQ About Frequently Asked Questions](https://blog.kindel.com/2018/11/18/a-faq-on-frequently-asked-questions/)
- [Be Either an App or a Platform, Not Both](https://blog.kindel.com/2011/08/24/be-either-an-app-or-a-platform-not-both/)
- [Building For The Robots](https://blog.kindel.com/2026/05/26/building-for-the-robots/)

# Press Release

**FOR IMMEDIATE RELEASE**
**Fall 2026**
**Durango, CO**

## Silico proves `Prompt for metal` Actually Works

**Durango, CO** — Grady had raised money to build Quilan and spent it on contract manufacture in Asia. The prototype existed. Field trials did not. He is not a software guy. Software was the stall.

Then:

> "I met Tig, and he showed me Silico. With just Claude Code on my Mac, I had the device working end-to-end the next day, and in a potential customer's hand the day after that. Silico is now a foundational piece of our company's technology."
> — Grady, CEO and Founder of Quilan

That is the product experience of **silico** (github.com/tig/silico). Not a new MCU religion. Not "hire an embedded team and wait a quarter." **Prompt for metal**: Claude Code on a Mac, host-honest done, board in a real hand on a two-day clock.

> **What we work backwards from:** a non-software founder (or vertical lead) with hardware in hand unblocks end-to-end device software with an agent in about a day, and puts that device with a potential customer the day after, with silico remaining foundational to how the company ships edge thereafter.

Tig Kindel today also announced that three GCUs share that spine: **Zakalwe**, **Quilan**, and **Sma** ([codenames for now](./gcu-codenames.md)). None is "the silico product." Each is a **GCU**: one shippable edge app with private domain logic and a life after the bench. Silico is not a GCU and not a company brand.

The engineering proof under the hood is the same story. Zakalwe's application firmware was written **entirely by AI agents**. The detailed product and software spec was written by agents from a rough domain brief. Tig is not a Pi expert and is not the electrical designer of that product. He owns judgment, contracts, and whether the host gate is green. Agents write the code. That is lived practice, not aspiration.

"Software is no longer a moat. Agents write the code. Edge that just works is hard. Vertical orientation is the future," said Tig Kindel. "Silico enables prompting for metal: the hard, boring stuff, gets done by AI and lands on devices reliably, safely, and repeatedly. Three different products in the field is the first proof the spine is real. Ask me later whether the rest of the world agrees."

### Availability

Quilan, Zakalwe, and Sma are available to their respective customers or field programs as of this release window. Silico itself is open source at github.com/tig/silico. Product domain, PCB, brands, and vertical IP remain with each product line.

End customers install or update with a short host path that finds the board, loads the application, and verifies version identity. "It worked on my COM port" is not a release criterion.

### Pricing

Each GCU is priced as a product. Silico is free under **Apache-2.0**. There is no silico SKU you must buy to use a GCU.

### How it works

**Day 1.** Grady opens a coding agent on his Mac, points it at silico, and works against a real board on USB (with host simulation in the loop). By the end of the day the device runs end-to-end and the host gate is green.

**Day 2.** The same path produces a prototype unit for a real customer in an **alpha** trial — early feedback, not a polished ship. Silico is how the team proves builds and updates the device.

**A month later.** Alpha feedback is in. Grady ships **beta** units to more customers with a hardened update path and the operational maturity that comes from real field use. Silico remains the spine through alpha and beta.

### How it works for the end customer

1. **Alpha:** receive a prototype; try it; send feedback.
2. **Beta:** receive a later unit built with that feedback and a production-minded update path.
3. When firmware changes, run the product's short update path. They never need to know the word silico.

# FAQ

Answers marked **open** are deliberately unanswered. Prefer a hard open over a soft lie.

## 1. What are we working backwards from?

Exactly this:

> "I met Tig, and he showed me Silico. With just Claude Code on my Mac, I had the device working end-to-end the next day, and in a potential customer's hand the day after that. Silico is now a foundational piece of our company's technology."

If a feature, doc, or process does not make that sentence more true (for Grady, for me, for the next vertical founder), it is not v1 work.

## 2. Why is this important to you (Tig)?

Because that two-day path is the only customer experience that matters for silico v1, and I know how rare it is.

Skin in the game: Media Center, Home Server, Phone, Echo, Control4 (device ops at scale; Echo toward continuous deploy with rollback). Live experiment: agents wrote Zakalwe firmware line for line and the detailed spec from a rough brief; I am not the Pi or electrical expert. Judgment and host-first done are mine. Typing firmware is not.

If Grady still needs a software guy and a quarter to move, **Prompt for metal** is a slogan. If only I can run the two days, we are not done.

Load-bearing tenets: [tenets.md](./tenets.md). Especially **Prompt for metal**, **Agents write the code**, **Agents operate the host path**, **Make it better than you found it**, **Vertical teams are the customer**.

## 3. What is silico, in one sentence?

The open spine that makes Grady's two days true: Claude Code on a Mac, device end-to-end tomorrow, potential customer's hand the day after, silico still foundational after that.

## 4. What does Day 1 really look like?

The checklist for Grady, or anyone who finds `github.com/tig/silico` and wants Day 2 to be possible. Order matters. Agent-facing detail lives in [AGENTS.md](../AGENTS.md).

**You need before you start**

1. A Mac or PC with internet.
2. Hardware that can run the GCU (for RP2040-class: board + USB data cable).
3. A rough idea of what the product must do (domain judgment). Silico will not invent your moat.
4. A GitHub account. CI and a durable GCU repo need a real remote.
5. Access to a coding agent (CLI or IDE). Examples: Claude Code, Grok Build, GitHub Copilot, OpenAI Codex.

**Account and tools**

6. Create a GitHub account if needed. Enable 2FA. You will create a **private** product repo here.
7. Start the agent and prompt: `See https://github.com/tig/silico. Follow the getting started instructions for agents.` The agent **helps the operator** (see [AGENTS.md](../AGENTS.md)): installs prerequisites, walks auth step by step, does not assume shell or first-flash literacy, and creates or selects a private GCU repo.
8. Agent and human confirm setup is complete before hardware work. Do not skip to flashing. Do not dump unexplained command lists on the human.

**Talk to real hardware**

9. Agent prompts the human to plug the device into USB, then configures until the board shows a **distinct, documented blink pattern** (green if the board has a color LED; otherwise a clear on/off pattern a novice can recognize) and reconnect is repeatable. If the board needs a runtime the first time (for example MicroPython UF2), the agent steps the human through it once per board, not on every app change.
10. Agent ensures the GCU GitHub repo has CI/CD. It prompts the human to open a GitHub issue titled roughly: `Change the firmware blink pattern (e.g. solid vs blink, or green vs red if RGB)`. When that issue exists, the agent implements it so CI is green **and** the real device behavior changes. That is the first proof of host gate + metal together.

**Make the device true (still Day 1)**

11. Human points the agent at domain intent docs (what the product must do). Agent writes or updates detailed specs, automated unit and smoke tests, and `firmware/` under test-first and host-first rules. Agent also creates a staged plan as cross-linked, tagged GitHub Issues for proprietary functionality.
12. Agent runs the named host gate locally until green. Red means not done. Do not "just flash it."
13. Agent and human iterate end-to-end on the bench (sim first if helpful, then metal) until behavior matches domain judgment and the host gate stays green.
14. Commit and push. CI green on GitHub matches local green. Humans file change requests as GitHub Issues at any time.

**Day 1 exit criteria (enables Day 2)**

15. Device works end-to-end on the bench.
16. Host gate green locally and on GitHub.
17. Version on device matches host.
18. One documented update command a non-expert can re-run tomorrow morning.
19. Silico remains a pinned host dependency in the GCU (foundational, not a copied script pile).

**Day 2 (alpha):** same update path; prototype to a real customer for alpha feedback — not beta polish. If Day 1 skipped GitHub, CI, pin, gate, or real USB metal, Day 2 is a laptop demo, not a company foundation. Full update-integrity suite is **not** a Day 2 requirement (that is the month-later beta horizon; see silicov1 and the integrity spike).

**A month later (beta):** feedback incorporated; more customers get beta-class units. Integrity protection (definition TBD — spike), optional self-hosted metal CI, and related hardening belong here.

**Split to remember:** `firmware/` → metal only. Silico package → Mac and CI only. Product domain stays private in the GCU.

## 5. Who is Grady?

CEO and Founder of Quilan. Not a software guy. Raised money, Asia-built prototype, software and field trials stalled. The person in the sentence we work backwards from.

## 6. What problem does silico refuse to solve?

The unicorn's core product. Vertical domain truth is their moat. Silico refuses to own it. Silico owns gobbledygook: prove on host, install, identify, recover, prompt agents without folklore.

## 7. What are the three GCUs?

1. **Zakalwe** — closed-loop control GCU. No internet requirement. First extraction source; agent-authored firmware is the existence proof.
2. **Quilan** — slow field logger GCU. Only starter that needs internet and phone-home (app-owned in v1, not silico spine).
3. **Sma** — sleep-friendly mesh node GCU. Local mesh is product IP; not WAN phone-home via silico.

Legend: [gcu-codenames.md](./gcu-codenames.md). Do not expand codenames to brands or markets in public silico docs.

## 8. Who is the customer of each GCU?

**open.** Name the buyer, the installer, and the person who suffers if the unit lies. Do not collapse them into "users." Keep real brands out of public silico docs.

## 9. Who is the customer of silico?

Near term: me, shipping three GCUs with agents under contracts I write; partners who supply domain rough specs (Galahad-shaped).

Target: vertical teams (SpaceX / Stoke / Figure / Anduril shaped) that need edge in the solution, move fast with agents, and will not staff a permanent device-ops cult. Grady (Quilan) is that customer in one quote.

End customers of Zakalwe, Quilan, or Sma never have to know silico exists.

## 10. Is silico an app or a platform?

Today it is a builder tool (an app for people who ship GCUs) governed by tenets. It is not a multi-sided platform under the Gates line until economic value to everyone using it exceeds value I capture. See [Virtuous Cycles, Platforms, Flywheels, Snowballs, and Tidal Waves](https://blog.kindel.com/2021/03/30/virtuous-cycles-platforms-flywheels-snowballs-and-tidal-waves/) and [Be Either an App or a Platform, Not Both](https://blog.kindel.com/2011/08/24/be-either-an-app-or-a-platform-not-both/).

## 11. Why not call this a platform in the press release?

Because I still stand by 2011. Calling a tool a platform before the sides show up loses focus. The PR names three apps, a spine, agent-authored firmware as proof, and honest language under **Extract, then open**.

## 12. What are the Principles for this release?

The Silico tenets ([tenets.md](./tenets.md)). Ties broken most often by:

1. **Agents write the code.** Hand-authored firmware is not the default path.
2. **Agents operate the host path.** Help the operator; do not assume Git, COM ports, first flash, or agent UI tricks.
3. **Make it better than you found it.** Friction that forced a guess becomes an `AGENTS.md` fix or a `tig/silico` issue, not chat-only lore.
4. **Prompt for metal** and **Host first.** Green host command is done; flash confirms.
5. **Apps stay apps.** Domain IP stays private.
6. **Extract, then open.** Second GCU forces promotion; three field GCUs prove extraction only.

## 13. What are the Priorities (in order)?

1. Three GCUs actually in field service (not bench heroes).
2. Shared install/update/verify path end customers can run.
3. Host CI that matches "done," including for agent-authored changes (the only kind we expect).
4. AGENTS.md and anti-patterns so models stop reviving dead mistakes.
5. Public silico repo that is not a dump of private product trees.
6. Honest language: extraction proven; external adoption not yet.

## 14. What is deliberately out of scope for silico v1 / Fall 2026?

1. Built-in internet and phone-home **as silico spine features** (Quilan may do WAN in the *app*).
2. Claiming external adoption or "industry default."
3. A full v2 narrative (see FAQ 40 for longer-term vision in one place).
4. Arduino-class plates as a v1 deliverable (room in the architecture; build when a GCU forces it).
5. Paid silico support, multi-tenant cloud twin, "silico certified" marketing.

## 15. How will we describe this in one breath?

Tomorrow the device works end-to-end with Claude Code on your Mac. The day after, it is in a potential customer's hand. Silico stays how you ship edge after that.

## 16. What is the plan for geographic roll out?

**open.**

## 17. How does this compare to Embedder, Simantic, ESPHome, PlatformIO, etc.?

Those are real tools. Most stop at an **expert developer's desk** or lock you into a **hub/cloud/module** story. Silico's wedge is the combination, not any single feature:

1. **Open spine** — not a closed "Claude Code for embedded" SaaS.
2. **Host-first done** — green named gate before metal counts; built for **agent-authored** firmware.
3. **Help the operator** — non-software founders (Grady), not only career embedded engineers.
4. **Customer path** — install/update/version identity after Day 1, through alpha and beta.

**PlatformIO / raw MicroPython / ESP-IDF** are fine *inside* a GCU. They are build runtimes, not the Day 1→Day 2 product loop.

**ESPHome** proved non-programmer firmware UX at hobby/smart-home scale. Silico aims that operator energy at **vertical product** GCUs, not YAML-for-the-home as the product.

**Embedder / Simantic / similar** (agent + firmware / sim) are the 2026 comparison class. Where they optimize expert velocity or simulation, silico optimizes **open doctrine + operator bedside manner + customer update path**. Use them as complements when they help; they are not a substitute for the spine.

No full SWOT in this FAQ. Landscape shifts; the wedge should not.

## 18. What is the thing you think hardest about?

Whether "in the field" is honest for all three GCUs by Fall 2026, and whether I will confuse "agents shipped my apps" with "vertical unicorns will adopt this." Those are different proofs. Also whether host gates stay honest when the agent is confident and wrong.

## 19. Risk: What are the riskiest parts of this?

1. Soft "field" definition (one friendly pilot counts).
2. Claiming external proof when only extraction (or only Zakalwe agent-authorship) is proven.
3. Leaking proprietary GCU logic into silico to win demos.
4. Install UX that still requires git clone and a developer onboarding ritual.
5. One GCU's timing or power needs blowing shared assumptions.
6. Agents shipping confident wrong firmware because anti-patterns were never written down.
7. Humans "helping" by bypassing the host gate and reintroducing folklore.
8. Building spine features vertical teams do not care about while the gate is still soft.

## 20. Risk: Impact, likelihood, exposure?

**open.**

## 21. Risk: Mitigations?

1. One-sentence "field" definition per GCU before more spine code.
2. Label extraction vs external proof every time we talk (**Extract, then open**).
3. CODEOWNERS and review on anything moving private app to silico.
4. Release zip for at least one GCU (no git) before declaring install done.
5. Domain stays private; only lifecycle machinery promotes.
6. Host gate in CI on every GCU; no honor system; no "I flashed it on my desk."
7. Anti-pattern files next to AGENTS.md; agent-written code is the default path, not a side quest.
8. Keep the Zakalwe story honest: non-expert human, agent-authored firmware, rough brief from Galahad.

## 22. What IP will we create?

Private: each GCU's firmware domain, PCB, mechanical, brand.
Open (tig/silico): spine, plates, docs, agent contracts, non-secret examples.
**open:** license choice and patent posture.

## 23. What tech do we buy, license, use, or invent?

Use: MicroPython, mpremote, pytest, GitHub Actions, KiCad where products need boards.
Invent: host-first contracts, install/verify protocol, agent prompt surface, discipline that keeps apps from becoming platforms.
Buy/license: **open.**

## 24. What cloud services will be required?

None for silico v1. Quilan may phone home on its own app dime. Zakalwe does not need WAN. Sma local mesh is not cloud. Continuous deploy with automatic rollback for fleets is longer-term vision (FAQ 40), not this PR.

## 25. What device software will be required?

Per GCU: application firmware on device runtime (MicroPython on RP2040-class for the first three unless a GCU forces a pivot). Agents write it. Shared: version identity, harness or self-test signature, HAL-shaped I/O for host sim.

## 26. How will we measure success?

Primary: can a Grady-shaped founder reproduce the path without Tig in the room?
- Day 1: agent on Mac, real USB device (+ sim), end-to-end, host gate green.
- Day 2: prototype with a **real customer for alpha** (not beta).
- ~1 month later: beta units for more customers; integrity posture per spike (not Day 2 scope).
- Ongoing: silico still foundational (not a one-off demo).

Secondary: three GCUs on one spine; agent-authored firmware under contracts; public spine usable without private trees.
Not yet: strangers adopt without meeting Tig.
**open:** product-line revenue is not silico's scoreboard.

## 27. What metrics will you track?

Candidates: host CI green rate; time merge to verified device version; failed install rate; field returns tied to firmware; silico promotions driven by a second GCU; fraction of firmware commits that are agent-authored; agent changes that pass host gate without human code rewrite.
**open:** pick the few that change behavior.

## 28. Why not only ship Zakalwe?

Because **Vertical teams are the customer** and **Prompt for metal** are not one vertical. Quilan and Sma force extraction. If they die, silico should still have made Zakalwe more shippable and agent contracts more honest. If they live, gobbledygook was paid down once.

## 29. What customer segments will these products NOT attract?

**open** per GCU. Hostile version: who do we tell "no"?

## 30. Does "in the field" mean paying strangers or my own sites and benches?

**open.** Write the bar so a skeptic cannot move it after the fact.

## 31. Will end customers need Python installed?

Zakalwe path often yes today. Fall 2026 ambition: at least one GCU has a path that is not developer onboarding.
**open:** L1 release zip vs L2 installer.

## 32. What happens when the wrong USB device is on the machine?

Updater prefers known VIDs, allows explicit port, fails closed with a readable error. "connect auto" is not the product story. This is gobbledygook vertical teams should not re-learn.

## 33. How do agents know they are done?

AGENTS.md names the host command that must be green. Device flash is confirmation, not proof. That is **Prompt for metal** and **Host first**. Without that, "agents write the code" is cosplay.

## 34. How do humans who are not embedded experts know they are done?

Same gate. Same version verify. Same anti-patterns. The point of Zakalwe is that the human did not need Pi literacy to ship. If the process reintroduces "ask the firmware person," we failed.

## 35. What is the naming plan?

Spine: silico (github.com/tig/silico).
Product class: GCU (GCV later if needed).
Public product references: Zakalwe, Quilan, Sma only.
Commercial brands: **open** per app; not silico sub-brands.

## 36. HW: SKU plan?

**open** per product.

## 37. HW: Regulatory?

**open.** Per product class. Keep product-specific lists out of public silico docs.

## 38. HW: EOL for key components?

**open.**

## 39. What is the relationship between this doc and silicov1.md?

[silicov1.md](./silicov1.md) is the buildable spine spec for three Pi-class GCUs. [tenets.md](./tenets.md) is the Principle set. This WB doc is the v1 customer-facing ambition and FAQ forcing function. If they disagree, fix one.

## 40. What is the longer-term vision?

Not a second full WB (yet). Direction under the same tenets:

1. Silico becomes the boring default for vertical teams who **Prompt for metal** instead of staffing device-ops cults.
2. Multi-target spine when real GCUs force it (for example Arduino-class plates), not before.
3. Phone-home and network patterns **in silico** when a second GCU needs what Quilan already does in app code; USB host path remains always available.
4. Echo-shaped continuous deploy with automatic rollback for fleets, only after host-first and version identity are boring.
5. External scoreboard: independent GCUs and vertical orgs, not star count.
6. Still not a company product line; still apps stay apps; still no domain moat in the open spine.

v1 success does not require any of that. v1 requires three field GCUs, agent-honest gates, and a spine extracted without cosplay. Revisit a v2 WB when external proof or a second forcing function demands it.

## 41. Is silico a company product?

No. Tig Kindel's open-source spine under the Silico tenets. Private GCU apps ship under whatever brand each requires.

## 42. When are the tenets proven externally?

Not when three GCUs ship. When silico works in a way I will shout about, and either others adopt it for vertical edge work or a clearer better thing forces better tenets. Until then: under test. Zakalwe already proves agents can write the firmware for a non-expert human. That is necessary and not sufficient.

## 43. When is this doc done?

When a hostile reader can state the two-day Grady experience in one breath, see how every priority serves it, still tell extraction from external proof apart, and not invent a platform cosplay or leak product brands.
