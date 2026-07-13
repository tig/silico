"""Boot entry: init + tick. No hardware at import time."""

from version import FW_NAME, FW_VERSION


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


def main():
    state = init()
    while True:
        tick(state)


if __name__ == "__main__":
    main()
