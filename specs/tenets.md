# Silico Tenets

Unless you know better ones.

Tenets are the written rules that distinguish good behavior from unwelcome behavior for this endeavor. They are the Principle part of a [5Ps plan](https://blog.kindel.com/2011/06/14/the-5-ps-achieving-focus-in-any-endeavor/). Craft and debate them; do not treat them as stone. See [Tenets](https://blog.kindel.com/2020/02/10/tenets/).

**Foundational** tenets say why Silico exists and what value it delivers. **Aspirational** tenets say how we intend to operate even when we are not there yet.

## Foundational

1. **Software is not the moat.** Generic software no longer differentiates. Customer value lives in the vertical product, the field loop, and the data that only that product creates. When forced to choose between polishing a clever library and shipping a GCU that works in service, ship the GCU.

2. **Agents write the code.** Day-to-day software, including firmware, detailed specs, and tests, is written and maintained by AI agents. Humans own judgment, prompts, contracts, anti-patterns, and the call on what "done" means. You do not need to be the Pi expert or the electrical expert to ship a GCU. A workflow that requires the human to author the firmware by hand is a design failure.

3. **Agents operate the host path.** Agents run the gobbledygook: machine setup, GitHub auth and CI, package pins, first firmware/runtime on the board, port discovery, deploy, version verify, and the issue→gate→metal loop. The human is an **operator to help**, not a presumed expert. Do not assume they know how to flash initial firmware, pick a COM port, run `gh`, or type shell the agent cannot run. Guide them step by step; do the work the agent can do; never dump a wall of unexplained commands.

4. **Make it better than you found it** (also **[compound](./lexicon.md#compound)**). Anytime something does not go smoothly and an agent must guess, correct, reverse, or research where a simple edit to Silico's `AGENTS.md` (or other agent-facing docs) or a bug fix to the infrastructure would make the next agent faster, fix it. Prefer a small PR when you can; otherwise file a clear issue on `tig/silico`. Do not leave the recovery only in chat. Tribal knowledge is a regression. **Compound** is the short agent-facing name for this tenet.

5. **Edge that just works is hard.** Devices, install, identity, recovery, and field ops stay hard even when agents write the code and run the host path. We invest in that gobbledygook so vertical teams do not.

6. **Vertical teams are the customer.** Builders in the SpaceX, Stoke Space, Figure, and Anduril pattern need edge devices inside a vertical solution. They do not want a device-ops priesthood. Pure cloud SaaS with no metal is not our customer.

7. **Prompt to metal.** Silico exists so teams can prompt agents such that what they *care about* lands on edge devices reliably, safely, and repeatedly. The experience we work backwards from: agent on a Mac with a hardware spec, device working end-to-end in a few hours, field test the day after, Silico still foundational after that. Host gates, version verify, and agent docs are the product surface for that prompt. Folklore is not. The human's job is domain judgment and confirmation, not typing C or MicroPython into a blank file or memorizing serial folklore.

8. **Default is a product choice, not a quality ranking.** Default runtime means "open this door first for most GCUs," not "this language is better." Supported backends share the same excellence bar. A weak path is unfinished Silico, not a ranking.

## Aspirational

9. **Host first.** Done means the host gate is green before anyone treats a device flash as proof. Metal confirms. Metal does not define done. That is how a non-expert knows the agent's work is true.

10. **Apps stay apps.** Domain IP stays private to each GCU. Silico is the spine, not the product, not a company SKU, and not platform cosplay. Promote a pattern into Silico only when a second GCU needs it. Public Silico docs name starter GCUs by codenames; short published product shape is OK when the owner chooses (see [gcu-codenames.md](./gcu-codenames.md)).

11. **Extract, then open.** We grow the spine from real field GCUs, not from imaginary third parties. Three GCUs in the field prove extraction. Adoption and "it actually works" prove the rest. We do not claim the second proof when we only have the first.
