"""Device HAL backend — the only plate module allowed to import ``machine``.

Listed in silico.toml ``[hal].allow_machine``. Host tests never import this
module; they inject ``sim.hal_double.FakeHal`` (or a plant) into ``main.init``.
"""

from __future__ import annotations

# Seeed XIAO RP2040 user green LED (USER_LED_G). Active-low.
_LED_PIN = 16


def make_board_hal():
    """Construct the on-metal HAL. Imports machine only when called on device."""
    from machine import Pin  # type: ignore
    import time

    pin = Pin(_LED_PIN, Pin.OUT)
    pin.value(1)  # off when active-low

    class BoardHal:
        def set_led(self, on: bool) -> None:
            pin.value(0 if on else 1)

        def ticks_ms(self) -> int:
            return int(time.ticks_ms())

        def sleep_ms(self, ms: int) -> None:
            time.sleep_ms(int(ms))

    return BoardHal()
