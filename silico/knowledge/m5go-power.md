# M5GO / M5Stack Core v2.7 power button (self-improving)

Hardware power path for **M5GO IoT Kit v2.7** and similar Core v2.7 units with battery base. Not product UI.

## Battery (USB unplugged)

| Action | Control |
|--------|---------|
| **Power on** | **Single-click** the red side power button |
| **Power off** | **Quick double-click** the red side power button |

**Long-press is not the off gesture** on this family. Teaching long-press off causes false “power is broken” reports.

## USB plugged in

USB power typically **keeps the unit on** and charges the battery. Double-click off may not fully behave as on pure battery. Unplug USB first for a clean battery-style off.

## Hardware battery isolate

Some v2.7 units have a **small switch on the bottom/back** that isolates the battery pack (`0` = disconnected). Use as a hard kill when software/button off is confusing after erase or odd PMIC state.

## After full flash erase

With no firmware, the power button still follows **hardware** rules above. Odd boot loops can look like “won’t turn off”; try double-click, then battery switch, then USB unplug.

## Agent checklist

1. When the operator asks how to power off an M5GO / Core v2.7: **double-click**, not long-press.
2. Do not invent product soft-power that fights the red button.
3. Extend this file if a later board revision documents a different gesture.
