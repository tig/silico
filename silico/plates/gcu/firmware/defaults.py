"""Shipped product defaults — the configuration the metal build actually runs.

Host tests that inject different gains/setpoints prove a *different* product.
At least one sim scenario must import this module and drive the control path
with these values unmodified (see silico product-path / AGENTS).
"""

# Status blink period on device (ms between toggles).
TICK_SLEEP_MS = 250

# Seeed XIAO RP2040 user green LED pin (active-low on board HAL).
LED_PIN = 16
