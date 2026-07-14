"""Boot entry: init + tick. Host-import safe — no ``machine`` in this module.

Device starts the loop only when executed as ``__main__`` (MicroPython boot).
Host tests import ``init`` / ``tick`` and inject a fake HAL.
"""

from defaults import TICK_SLEEP_MS
from version import FW_NAME, FW_VERSION


def init(hal=None):
    return {
        "hal": hal,
        "fw_name": FW_NAME,
        "fw_version": FW_VERSION,
        "tick_count": 0,
        "led_on": False,
        "tick_sleep_ms": TICK_SLEEP_MS,
    }


def tick(state):
    state["tick_count"] = state["tick_count"] + 1
    state["led_on"] = not state["led_on"]
    hal = state.get("hal")
    if hal is not None and hasattr(hal, "set_led"):
        hal.set_led(state["led_on"])
    return state


def main():
    # Import device backend only on the metal boot path (not at host import).
    from hal_board import make_board_hal

    state = init(hal=make_board_hal())
    while True:
        tick(state)
        # Cadence comes from the shipped defaults, never a literal in this module.
        sleep_ms = state.get("tick_sleep_ms", TICK_SLEEP_MS)
        hal = state.get("hal")
        if hal is not None and hasattr(hal, "sleep_ms"):
            hal.sleep_ms(sleep_ms)
        else:
            try:
                import time

                time.sleep(sleep_ms / 1000.0)
            except ImportError:
                pass


# MicroPython executes main.py as __main__. Host importlib load uses name "main".
if __name__ == "__main__":
    main()
