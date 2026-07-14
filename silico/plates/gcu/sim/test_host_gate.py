"""Host gate: firmware modules load without a board; HAL seam stays honest."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIRMWARE = ROOT / "firmware"
SIM = ROOT / "sim"


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


def _load_sim(name: str):
    path = SIM / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SIM))
    try:
        spec.loader.exec_module(mod)
    finally:
        if sys.path and sys.path[0] == str(SIM):
            sys.path.pop(0)
    return mod


def test_version_identity_present():
    version = _load("version")
    assert isinstance(version.FW_NAME, str) and version.FW_NAME
    assert isinstance(version.FW_VERSION, str) and version.FW_VERSION.count(".") >= 2


def test_hal_contract_importable_without_machine():
    # Contract module must not touch hardware.
    hal_mod = _load("hal")
    assert hasattr(hal_mod, "Hal")


def test_main_init_tick_with_fake_hal():
    main = _load("main")
    fake = _load_sim("hal_double").FakeHal()
    state = main.init(hal=fake)
    main.tick(state)
    assert state["led_on"] is True
    assert fake.led is True
    assert state["fw_name"]
    assert state["fw_version"]


def test_host_hygiene_gate():
    """Silico hygiene: deploy set host-importable; only allowlisted stems use machine."""
    from silico.host_hygiene import run_hygiene

    report = run_hygiene(ROOT)
    assert report.ok, "\n".join(report.lines)
