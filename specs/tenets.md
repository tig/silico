# Silico Tenets

Unless you know better ones.

Tenets are the written rules that distinguish good behavior from unwelcome behavior for this endeavor. They are the Principle part of a [5Ps plan](https://blog.kindel.com/2011/06/14/the-5-ps-achieving-focus-in-any-endeavor/). Craft and debate them; do not treat them as stone. See [Tenets](https://blog.kindel.com/2020/02/10/tenets/).

**Foundational** tenets say why silico exists and what value it delivers. **Aspirational** tenets say how we intend to operate even when we are not there yet.

## Foundational

1. **Software is not the moat.** Generic software no longer differentiates. Customer value lives in the vertical product, the field loop, and the data that only that product creates. When forced to choose between polishing a clever library and shipping a GCU that works in service, ship the GCU.

2. **Agents write the code.** Day-to-day software, including firmware and detailed specs, is written and maintained by AI agents. Humans own judgment, prompts, contracts, anti-patterns, and the call on what "done" means. You do not need to be the Pi expert or the electrical expert to ship a GCU. A workflow that requires the human to author the firmware by hand is a design failure.

3. **Edge that just works is hard.** Devices, install, identity, recovery, and field ops stay hard even when agents write the code. We invest in that gobbledygook so vertical teams do not.

4. **Vertical teams are the customer.** Builders in the SpaceX, Stoke Space, Figure, and Anduril pattern need edge devices inside a vertical solution. They do not want a device-ops priesthood. Pure cloud SaaS with no metal is not our customer.

5. **Prompt for metal.** Silico exists so teams can prompt agents such that what they *care about* lands on edge devices reliably, safely, and repeatedly. The experience we work backwards from: Claude Code on a Mac, device working end-to-end the next day, potential customer's hand the day after, silico still foundational after that. Host gates, version verify, and agent docs are the product surface for that prompt. Folklore is not. The human's job is the prompt and the judgment, not typing C or MicroPython into a blank file.

## Aspirational

6. **Host first.** Done means the host gate is green before anyone treats a device flash as proof. Metal confirms. Metal does not define done. That is how a non-expert knows the agent's work is true.

7. **Apps stay apps.** Domain IP and product brands stay private to each GCU. Silico is the spine, not the product, not a company SKU, and not platform cosplay. Promote a pattern into silico only when a second GCU needs it. Public silico docs refer to starter GCUs only by codenames ([gcu-codenames.md](./gcu-codenames.md)).

8. **Extract, then open.** We grow the spine from real field GCUs, not from imaginary third parties. Three GCUs in the field prove extraction. Adoption and "it actually works" prove the rest. We do not claim the second proof when we only have the first.
