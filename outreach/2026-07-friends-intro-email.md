# Friends intro email (July 2026)

Audience: friends and trusted contacts, asked for opinions, interest, and referrals.
Voice: per Tig's writing style guide. Send as email or DM; the text below is the message.

## Silico: Prompt for metal

I assert three things.

Software is dead as a moat. AI agents write the code now, and anything my agent can write, your agent can write too. Second, edge devices that just work are still hard; none of the USB port roulette, first-flash rituals, or field update pain got easier just because code got cheap. Third, vertical integration is the future. The winners will be domain people who put devices inside a solution they own end to end, and they will not staff a device-ops priesthood to do it.

I tested this on a real product. Zakalwe is a drop-in replacement for the analog idle control module in pre-1987 BMWs, built on a $4 RP2040. AI agents wrote every line of the firmware, the detailed spec, and all of the CI/CD and update infrastructure. All of it from Galahad's rough spec. I am not a Raspberry Pi expert, and I did not design the electronics. My job was judgment: what the product must do, and what "done" means. The car idles smoother than it did new.

The firmware was the easy part. The hard part is the gobbledygook every hardware team reinvents badly: proving firmware works before it touches the board, an install and update path a normal human can run twice, and a device that cannot lie about what version it is running. That is what I am extracting from Zakalwe, in the open.

> **Silico** is an open spine for shipping edge products with AI agents: host-side proof gates, a customer install and verify path, and version identity. Your product's secret sauce stays yours. One rule holds it together: **host gate green means done; metal confirms.**

The sentence silico works backwards from (it has not happened yet; it is the bar):

> With just Claude Code on my Mac, I had the device working end-to-end the next day, and in a potential customer's hand the day after that.

Silico is not a company, not a platform, and not a subscription. I still stand by what I wrote in 2011: be an app or a platform, not both. Zakalwe is the first of three products on the spine. When all three are in the field, I will have proof. Until then I am not claiming anything I cannot show.

Does the two-day claim make you lean in, or roll your eyes? Have you watched hardware stall waiting on software? Who should I be talking to? Don't be shy.

github.com/tig/silico
