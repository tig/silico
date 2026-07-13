from silico.mpy_pin import (
    PLATE_DEFAULT_MPY_CROSS,
    parse_micropython_version,
    parse_mpy_cross_pin,
    pin_advice_lines,
    same_minor,
    suggest_mpy_cross_pin,
)


def test_parse_micropython_from_sys_version():
    text = "3.4.0; MicroPython v1.28.0 on 2026-04-06"
    assert parse_micropython_version(text) == "1.28.0"


def test_parse_mpy_cross_pin_rc():
    assert parse_mpy_cross_pin("1.28.0rc0.post2") == (1, 28, 0)
    assert parse_mpy_cross_pin("1.27.0.post2") == (1, 27, 0)


def test_same_minor():
    assert same_minor("1.28.0rc0.post2", "1.28.0")
    assert not same_minor("1.22.2", "1.28.0")


def test_suggest_128_uses_rc():
    assert suggest_mpy_cross_pin("1.28.0") == "1.28.0rc0.post2"


def test_plate_default_not_ancient():
    assert PLATE_DEFAULT_MPY_CROSS != "1.22.2"
    maj = parse_mpy_cross_pin(PLATE_DEFAULT_MPY_CROSS)
    assert maj is not None and maj[1] >= 27


def test_advice_warns_on_mismatch():
    lines = pin_advice_lines("MicroPython v1.28.0", "1.22.2")
    text = "\n".join(lines)
    assert "WARN" in text
    assert "1.28" in text
