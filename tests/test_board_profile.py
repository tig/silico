"""Board product-face pin packs and defaults.py candidate seed."""

from pathlib import Path

from silico.board_profile import (
    list_profiles,
    load_profile,
    profiles_root,
    resolve_profile_id,
    seed_defaults_candidates,
    show_profile_lines,
)
from silico.parts import load_parts


def test_profiles_root_ships_m5go_and_xiao():
    root = profiles_root()
    assert (root / "m5go.toml").is_file()
    assert (root / "xiao-rp2040.toml").is_file()


def test_list_profiles_includes_m5go():
    ids = {p.id for p in list_profiles()}
    assert "m5go" in ids
    assert "xiao-rp2040" in ids


def test_load_m5go_face_pins():
    p = load_profile("m5go")
    assert p.id == "m5go"
    assert p.defaults_candidates["LED_PIN"] == 15
    assert p.defaults_candidates["SPEAKER_PIN"] == 25
    assert "side" in p.product_face_summary.lower() or "strip" in p.product_face_summary.lower()
    assert p.product_face.get("led_pin") == 15
    assert p.product_face.get("speaker_pin") == 25
    # Full face pack (#79): display / buttons / I2C-IMU
    display = p.product_face.get("display")
    assert isinstance(display, dict)
    assert display.get("controller") == "ILI9342C"
    assert display.get("sclk") == 18
    assert display.get("bl") == 32
    buttons = p.product_face.get("buttons")
    assert isinstance(buttons, dict)
    assert buttons.get("btn_a") == 39
    assert buttons.get("btn_c") == 37
    i2c = p.product_face.get("i2c")
    assert isinstance(i2c, dict)
    assert i2c.get("sda") == 21
    assert "326.8" in str(i2c.get("temp_formula", ""))


def test_load_xiao_led_pin():
    p = load_profile("xiao-rp2040")
    assert p.defaults_candidates["LED_PIN"] == 16


def test_unknown_profile_raises():
    try:
        load_profile("not-a-board")
        assert False, "expected FileNotFoundError"
    except FileNotFoundError as e:
        assert "not-a-board" in str(e)


def test_resolve_profile_from_parts_toml(tmp_path: Path):
    (tmp_path / "parts.toml").write_text(
        """
[[part]]
id = "esp32"
name = "ESP32"
role = "mcu"
datasheet = "https://example.com/esp32.pdf"

[[part]]
id = "m5go-board"
name = "M5GO"
role = "board"
profile = "m5go"
docs = "https://docs.m5stack.com/en/core/m5go"
""",
        encoding="utf-8",
    )
    report = load_parts(tmp_path)
    assert report.ok
    assert resolve_profile_id(tmp_path) == "m5go"
    board = next(p for p in report.parts if p.role == "board")
    assert board.profile == "m5go"


def test_seed_defaults_dry_run_does_not_write(tmp_path: Path):
    fw = tmp_path / "firmware"
    fw.mkdir()
    defaults = fw / "defaults.py"
    defaults.write_text(
        'TICK_SLEEP_MS = 250\nLED_PIN = 16\n',
        encoding="utf-8",
    )
    lines, changed = seed_defaults_candidates(
        tmp_path, profile_id="m5go", yes=False
    )
    assert not changed
    assert any("dry-run" in l.lower() or "would" in l.lower() for l in lines)
    assert "LED_PIN = 16" in defaults.read_text(encoding="utf-8")
    assert "SPEAKER_PIN" not in defaults.read_text(encoding="utf-8")
    assert any("15" in l for l in lines)
    assert any("operator" in l.lower() for l in lines)


def test_seed_defaults_yes_writes_candidates(tmp_path: Path):
    fw = tmp_path / "firmware"
    fw.mkdir()
    defaults = fw / "defaults.py"
    defaults.write_text(
        '"""Shipped product defaults."""\n\nTICK_SLEEP_MS = 250\nLED_PIN = 16\n',
        encoding="utf-8",
    )
    lines, changed = seed_defaults_candidates(
        tmp_path, profile_id="m5go", yes=True
    )
    assert changed
    text = defaults.read_text(encoding="utf-8")
    assert "LED_PIN = 15" in text
    assert "SPEAKER_PIN = 25" in text
    assert "TICK_SLEEP_MS = 250" in text
    assert any("wrote" in l.lower() or "updated" in l.lower() for l in lines)
    assert any("confirm" in l.lower() or "operator" in l.lower() for l in lines)


def test_show_profile_lines_mention_candidates():
    lines = show_profile_lines(load_profile("m5go"))
    joined = "\n".join(lines)
    assert "LED_PIN" in joined
    assert "15" in joined
    assert "SPEAKER_PIN" in joined
    assert "25" in joined
    assert "display:" in joined
    assert "ILI9342C" in joined
    assert "buttons:" in joined
    assert "39" in joined
    assert "i2c:" in joined
    assert "326.8" in joined


def test_m5_core_knowledge_documents_mpu6886():
    from pathlib import Path

    from silico.board_profile import profiles_root

    # knowledge lives next to boards under silico/
    knowledge = Path(__file__).resolve().parents[1] / "silico" / "knowledge" / "m5-core.md"
    assert knowledge.is_file()
    text = knowledge.read_text(encoding="utf-8")
    assert "MPU6886" in text
    assert "326.8" in text
    assert "MPU6050" in text  # footgun callout
    assert "0x19" in text
    # profile pointer
    del profiles_root
