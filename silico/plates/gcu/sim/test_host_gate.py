"""Host gate: firmware modules load without a board."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIRMWARE = ROOT / "firmware"


def _load(name: str):
    path = FIRMWARE / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(FIRMWARE))
    try:
        spec.loader.exec_module(mod)
    finally:
        if sys.path and sys.path[0] == str(FIRMWARE):
            sys.path.pop(0)
    return mod


def test_version_identity_present():
    version = _load("version")
    assert isinstance(version.FW_NAME, str) and version.FW_NAME
    assert isinstance(version.FW_VERSION, str) and version.FW_VERSION.count(".") >= 2


def test_main_init_tick():
    # Import must not hang (device main() only runs when machine exists).
    main = _load("main")

    class FakeHal:
        def __init__(self):
            self.led = None

        def set_led(self, on):
            self.led = on

    hal = FakeHal()
    state = main.init(hal=hal)
    main.tick(state)
    assert state["led_on"] is True
    assert hal.led is True
