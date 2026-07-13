"""Boot entry: init + tick. No hardware at import time on the host."""

from version import FW_NAME, FW_VERSION

# Seeed XIAO RP2040 user green LED (USER_LED_G). Active-low.
_LED_PIN = 16
_TICK_SLEEP_S = 0.25


def init(hal=None):
    return {
        "hal": hal,
        "fw_name": FW_NAME,
        "fw_version": FW_VERSION,
        "tick_count": 0,
        "led_on": False,
    }


def tick(state):
    state["tick_count"] = state["tick_count"] + 1
    state["led_on"] = not state["led_on"]
    hal = state.get("hal")
    if hal is not None and hasattr(hal, "set_led"):
        hal.set_led(state["led_on"])
    return state


def _board_hal():
    try:
        from machine import Pin  # type: ignore
    except ImportError:
        return None

    pin = Pin(_LED_PIN, Pin.OUT)
    pin.value(1)  # off when active-low

    class BoardHal:
        def set_led(self, on):
            pin.value(0 if on else 1)

    return BoardHal()


def main():
    state = init(hal=_board_hal())
    try:
        import time

        sleep = time.sleep
    except ImportError:
        sleep = lambda _s: None
    while True:
        tick(state)
        sleep(_TICK_SLEEP_S)


# Device boot: start loop. Host imports must not hang (no bare main()).
try:
    import machine  # type: ignore  # noqa: F401

    main()
except ImportError:
    pass
