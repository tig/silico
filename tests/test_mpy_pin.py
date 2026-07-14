from pathlib import Path

from silico.mpy_pin import (
    PLATE_DEFAULT_MPY_CROSS,
    apply_mpy_cross_pin,
    parse_micropython_version,
    parse_mpy_cross_pin,
    pin_advice_lines,
    read_toml_mpy_cross,
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


def test_suggest_126_uses_published_post():
    # CR: bare 1.26.1 is not on PyPI; map to installable post builds.
    assert suggest_mpy_cross_pin("1.26.0") == "1.26.0.post2"
    assert suggest_mpy_cross_pin("1.26.1") == "1.26.1.post2"


def test_plate_default_not_ancient():
    assert PLATE_DEFAULT_MPY_CROSS != "1.22.2"
    maj = parse_mpy_cross_pin(PLATE_DEFAULT_MPY_CROSS)
    assert maj is not None and maj[1] >= 27


def test_advice_warns_on_mismatch():
    lines = pin_advice_lines("MicroPython v1.28.0", "1.22.2")
    text = "\n".join(lines)
    assert "WARN" in text
    assert "1.28" in text


def test_apply_mpy_cross_pin_updates_toml_and_req(tmp_path: Path):
    (tmp_path / "silico.toml").write_text(
        '[runtime]\nmpy_cross = "1.22.2"\nboard = "xiao-rp2040"\n',
        encoding="utf-8",
    )
    (tmp_path / "requirements-dev.txt").write_text(
        "pytest>=8\nmpy-cross==1.22.2\n",
        encoding="utf-8",
    )
    lines = apply_mpy_cross_pin("MicroPython v1.28.0", root=tmp_path)
    text = "\n".join(lines)
    assert "1.28.0rc0.post2" in text
    assert read_toml_mpy_cross(tmp_path) == "1.28.0rc0.post2"
    req = (tmp_path / "requirements-dev.txt").read_text(encoding="utf-8")
    assert "mpy-cross==1.28.0rc0.post2" in req
    assert "1.22.2" not in req


def test_apply_creates_files_when_missing(tmp_path: Path):
    apply_mpy_cross_pin("1.27.0", root=tmp_path)
    assert read_toml_mpy_cross(tmp_path) == "1.27.0.post2"
    assert "mpy-cross==1.27.0.post2" in (tmp_path / "requirements-dev.txt").read_text(
        encoding="utf-8"
    )
