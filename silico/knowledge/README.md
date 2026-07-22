# Host knowledge (self-improving)

**Not product domain.** This tree is board/host/runtime knowledge for agents on the silico spine: first-flash, USB-serial classes, audio peripherals, deploy recovery.

Product domain (idle control, drone songs, vehicle acceptance) stays in the **GCU** repo.

## When to open a file

| Task | Open |
|------|------|
| ESP32 / DAC / speaker / PWM tone / sample playback | [esp32-audio.md](esp32-audio.md) |
| SPI IPS color / INVON / partial paint | [esp32-lcd-ips.md](esp32-lcd-ips.md) |
| Large binary assets (PCM, images) deploy verify | [deploy-assets.md](deploy-assets.md) |
| M5GO / Core v2.7 power button | [m5go-power.md](m5go-power.md) |
| ESP32 USB-serial duplex / console lockout / UART0 | [esp32-usb-serial.md](esp32-usb-serial.md) |
| First-flash UF2 vs esptool | [first-flash.md](first-flash.md) |
| Index of topics | [INDEX.md](INDEX.md) |

Do **not** load every knowledge file into context. Open only the topic you need.

## Make it better (required loop)

When Day 1 or metal work forces you to **guess, reverse, or research** something that is **host/board-generic** (not one vertical product):

1. Prefer a durable fix in code (`ports.py`, `inspect`, `deploy`, plate) when it is a tool bug.
2. If it is durable **guidance**, add or extend a file under `silico/knowledge/` in the same PR or a follow-up.
3. Keep notes short, imperative, and free of customer/product codenames.
4. Link the knowledge file from [INDEX.md](INDEX.md).
5. Point agents here from AGENTS.md / `silico doctor` (already does).

Leaving recovery only in chat violates **Make it better than you found it**.

## What does not belong here

- Vertical GCU specs, acceptance rows, brand names
- Bedside operator-manners contract (lives in tig/bedside)
- Long essays that duplicate AGENTS Day 1 phase order
