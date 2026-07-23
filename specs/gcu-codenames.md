# GCU codenames

Unless you know better ones.

> **GCU** means **General Contact Unit**: one shippable edge **product** with end-user value, private domain logic, and an install/upgrade system. Silico is the open spine, not a GCU. (Culture-flavored label; not a ship or Mind name.)

Public Silico docs name the three starter GCUs by Culture-series **person** codenames (not ships, not Minds): **Zakalwe**, **Quilan**, **Sma**.

**Public** material may include a short product description, technical shape (MCU class, runtime, connectivity), and builder/company attribution when the owner chooses to publish it—see the root README **Real World Examples**. The codenames remain the public product names in Silico; a one-paragraph shape is intentional and is not a dump of private domain IP.

**Still private:** full proprietary specs, vehicle tables, field recipes, unreleased brands the owner has not published, and anything that would put product moat into the spine. Domain IP lives in the GCU repo (**Apps stay apps**). Agents must not invent extra brand or market detail beyond what this file and the README already state.

| Codename | Public shape |
|----------|--------------|
| **Zakalwe** | Closed-loop control module that upgrades classic BMW, Volvo, and Mercedes cars from the '80s, by [Holy Grail Labs](https://www.holygraillabs.com). No internet connectivity. Replicates a 1970s-era control device with more than 100 discrete logic parts. RP2040-class, MicroPython. Tens-of-Hz period; host plant for regression. USB path; no WAN need. |
| **Quilan** | Solar-powered field logger with environmental and atmospheric sensors and LoRaWAN cloud connectivity. ESP32-class, C. Sample/store on seconds-to-minutes periods. **Only starter that needs internet and phone-home** (app-owned in v1). |
| **Sma** | Tiny, battery-powered, sleep-friendly remote sensing and mesh-connected device. RP2040-class, MicroPython. Wake cycles, battery budget, neighbor radio as product IP. Local mesh is not WAN phone-home. |

Names after Iain M. Banks characters: Cheradenine Zakalwe, Quilan (*Look to Windward*), Diziet Sma.

When adding further examples to public Silico docs, keep the same bar: codename (or agreed public name) + short published shape; no private domain dump.
