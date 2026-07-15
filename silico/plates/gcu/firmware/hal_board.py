"""Device HAL backend — the only plate module allowed to import ``machine``.

Listed in silico.toml ``[hal].allow_machine``. Host tests never import this
module; they inject ``sim.hal_double.FakeHal`` (or a plant) into ``main.init``.
"""

# No `from __future__` here: MicroPython has no __future__ module and this
# file runs on-device (tig/silico#46). The silico gate now enforces this for
# every deploy-set file.

# Pin comes from the shipped defaults, not a literal here. Two copies of a
# shipped value are two values: they drift, and the gate cannot tell which one
# the product runs.
from defaults import LED_PIN


def make_board_hal():
    """Construct the on-metal HAL. Imports machine only when called on device."""
    from machine import Pin  # type: ignore
    import time

    pin = Pin(LED_PIN, Pin.OUT)
    pin.value(1)  # off when active-low

    class BoardHal:
        def set_led(self, on: bool) -> None:
            pin.value(0 if on else 1)

        def ticks_ms(self) -> int:
            return int(time.ticks_ms())

        def sleep_ms(self, ms: int) -> None:
            time.sleep_ms(int(ms))

    return BoardHal()
