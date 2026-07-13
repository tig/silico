## Silico: Prompt for metal

I assert these things:

a) Software is no longer a moat; all software in the future will be written and maintained by AI.
b) Buildling edge devices that just work remains hard, even for AIs.
d) Venture capital is going into vertical itegration ala SpaceX, Stoke Space, Figure, and Andruil; not just products built from other's parts.
e) AI Native companies will move the fastest.

I have deep experience building edge devcies at scale, starting with Windows Media Center (almost pre-Internet), Windows Home Server, Windows Phone, Echo. Echo, and mulitple devices at Control4. For example, Echo exemplified "the cloud is just someone else's computer"; when I left Amazon we were approaching "Continous Deployment with automatic rollback" for Echo devices. At Control4, I transformed the engineering capabilty to enable this model for C4's touchscreens, remote controls, door stations, and more. 

In addition, recently, I've built WinPrint 3.x, MCEC 3.x, and much of the newer Terminal.Gui stuff in a AI Native way: I no longer open IDEs and I have no idea what the code looks like. All three work brilliantly, are easy to maintain (via AI), and are well engineered. 

Galahad and I are working on a new product for mid-80's euro cars: A replacement idle control module. The original Bosch device was analog and they all eventually fail due to solder joints failing, etc... Gally designed a digital solution around a Raspberry Pi (a $4 RP2040) where software would replicate what the old analog stuff did. My job has been to write the firmware. Last week (in less than a day's work), AI agents wrote every line of the firmware, the detailed spec, and all of the CI/CD and update infrastructure. All of it from Galahad's rough spec. I am not a Raspberry Pi expert, and I did not design the electronics. My job was judgment and edge device expertiese: what the product must do, and what "done" means. 

The firmware was the easy part. The hard part is the gobbledygook every hardware team reinvents badly: proving firmware works before it touches the board, an install and update path a normal human can run twice, and a device that cannot lie about what version it is running.

At the same time I was working on the ICM, two other serendipitous events occured: First, I started working with a solo-founder here in Durango who is building a ruggedized outdoor device based on a rasperrby pi and an hardware design he outsourced to Asia. Grady is technical-enough, but no software expert. He's struggled to find software expertise that could build the firmware. 

Second, Doug Hebenthal reached out to see if I could help him with a sound-sensing raspbeery pi device he's working on. He figured he could probably use AI to build the firmware, but guessed I might be able to do it more effectively.

This weekend I had an empiphany: I could generalize the idle control module solution into something that would make both Grady's and Doug's dreams come true.

I call it `silico`.

The hypothesis is: "Successful companies AI Native companies, moving fast, won't care about the goobbly-gook required to build/operate edge devices that are part of their solution. They will care about having a reliable way of prompting agents to ensure what the DO care about gets onto those edge devices reliably, safely, and repeatedly."

Silico is a test of that hyphothesis.

Software is dead as a moat. AI agents write the code now, and anything my agent can write, your agent can write too. Second, edge devices that just work are still hard; none of the USB port roulette, first-flash rituals, or field update pain got easier just because code got cheap. Third, vertical integration is the future. The winners will be domain people who put devices inside a solution they own end to end, and they will not staff a device-ops priesthood to do it. They will just use AI.

I am currently testing this on a the ICM by real starting clean, just using silico to guide the AIs. Once I do that, my plan is to ask Grady if he'd be willing to be "customer #2" and see how that goes. Then I'll apply it to Doug's product.

> **Silico** is an open spine for shipping edge products with AI agents: host-side proof gates, a customer install and verify path, and version identity. Your product's secret sauce stays yours. One rule holds it together: **host gate green means done; metal confirms.**

The sentence silico works backwards from (it has not happened yet; it is the bar):

> With just Claude Code on my Mac, I had the device working end-to-end the next day, and in a potential customer's hand the day after that.

Silico is not a company, not a platform, and not a subscription. I still stand by what I wrote in 2011: be an app or a platform, not both. I have 3 real-ish test products to test the spine. When all three are in the field, I will have proof. Until then I am not claiming anything I cannot show.

Does the two-day claim make you lean in, or roll your eyes? Don't be shy.

github.com/tig/silico
