from pathlib import Path

from silico.gate_c import check_hal_init_reachable, run_c_gate, scan_device_includes
from silico.product_path import run_product_path_check
from silico.scaffold import plate_root, scaffold


def _write_c_fixture(root: Path, *, bad_include: bool = False) -> None:
    (root / "silico.toml").write_text(
        """
[runtime]
language = "c"
chip = "esp32"
[host]
gate = "echo skip-host-build"
product_defaults = "include/gcu/defaults.h"
[hal]
allow_device_headers = ["hal_board"]
[deploy]
mode = "idf-flash"
project = "firmware"
""",
        encoding="utf-8",
    )
    (root / "include" / "gcu").mkdir(parents=True)
    (root / "include" / "gcu" / "defaults.h").write_text(
        "#ifndef D\n#define D\n#define TICK_SLEEP_MS 250\n"
        "typedef struct { int tick_sleep_ms; } gcu_defaults_t;\n"
        "extern const gcu_defaults_t GCU_DEFAULTS;\n#endif\n",
        encoding="utf-8",
    )
    (root / "src").mkdir()
    (root / "src" / "domain.c").write_text(
        '#include "gcu/defaults.h"\nconst int z = 1;\n',
        encoding="utf-8",
    )
    (root / "host").mkdir()
    (root / "host" / "test_defaults.c").write_text(
        '#include "gcu/defaults.h"\n'
        "int main(void) { return GCU_DEFAULTS.tick_sleep_ms == 250 ? 0 : 1; }\n",
        encoding="utf-8",
    )
    (root / "firmware" / "main").mkdir(parents=True)
    board = '#include "freertos/FreeRTOS.h"\nvoid board(void) {}\n'
    if bad_include:
        (root / "src" / "leaky.c").write_text(
            '#include "esp_system.h"\nvoid leak(void) {}\n',
            encoding="utf-8",
        )
    (root / "firmware" / "main" / "hal_board.c").write_text(board, encoding="utf-8")
    # HAL init reachable from app_main (gate checks this for language=c).
    (root / "firmware" / "main" / "main.c").write_text(
        "void app_main(void) {\n"
        "  gcu_hal_t *hal = gcu_make_board_hal();\n"
        "  gcu_state_t st;\n"
        "  gcu_init(&st, hal);\n"
        "  for (;;) { gcu_tick(&st); }\n"
        "}\n",
        encoding="utf-8",
    )


def test_scan_allows_hal_board_only(tmp_path: Path):
    _write_c_fixture(tmp_path, bad_include=False)
    fails = scan_device_includes(tmp_path)
    assert fails == []


def test_scan_rejects_device_header_in_src(tmp_path: Path):
    _write_c_fixture(tmp_path, bad_include=True)
    fails = scan_device_includes(tmp_path)
    assert fails
    assert any("leaky.c" in f for f in fails)


def test_c_gate_hygiene_ok(tmp_path: Path):
    _write_c_fixture(tmp_path)
    report = run_c_gate(tmp_path, run_command=False)
    assert report.ok, report.lines


def test_c_gate_hygiene_fail(tmp_path: Path):
    _write_c_fixture(tmp_path, bad_include=True)
    report = run_c_gate(tmp_path, run_command=False)
    assert not report.ok


def test_hal_init_reachable_plate_main():
    root = plate_root("gcu-c")
    fails = check_hal_init_reachable(root)
    assert fails == [], fails


def test_hal_init_fails_when_dropped(tmp_path: Path):
    _write_c_fixture(tmp_path)
    (tmp_path / "firmware" / "main" / "main.c").write_text(
        "void app_main(void) {\n  for (;;) { /* loop without HAL */ }\n}\n",
        encoding="utf-8",
    )
    fails = check_hal_init_reachable(tmp_path)
    assert fails
    assert any("gcu_make_board_hal" in f for f in fails)
    assert any("gcu_init" in f for f in fails)
    report = run_c_gate(tmp_path, run_command=False)
    assert not report.ok


def test_scaffold_gcu_c_gitignore_managed_components(tmp_path: Path):
    dest = tmp_path / "c-prod"
    scaffold(dest, plate="gcu-c")
    gi = (dest / ".gitignore").read_text(encoding="utf-8")
    assert "managed_components/" in gi
    assert "firmware/managed_components/" in gi


def test_product_path_c(tmp_path: Path):
    _write_c_fixture(tmp_path)
    report = run_product_path_check(tmp_path)
    assert report.ok, report.lines
    assert report.sim_refs >= 1


def test_product_path_c_fails_without_host_use(tmp_path: Path):
    _write_c_fixture(tmp_path)
    (tmp_path / "host" / "test_defaults.c").write_text(
        "/* no include */\nint main(void) { return 0; }\n",
        encoding="utf-8",
    )
    report = run_product_path_check(tmp_path)
    assert not report.ok


def test_product_path_c_fails_on_comment_only_symbol(tmp_path: Path):
    """Comments must not satisfy product-path (same honesty as Python AST gate)."""
    _write_c_fixture(tmp_path)
    (tmp_path / "host" / "test_defaults.c").write_text(
        '#include "gcu/defaults.h"\n'
        "/* use GCU_DEFAULTS someday */\n"
        "int main(void) { return 0; }\n",
        encoding="utf-8",
    )
    report = run_product_path_check(tmp_path)
    assert not report.ok
    assert any("FAIL" in line for line in report.lines)


def test_product_path_c_fails_on_bare_include(tmp_path: Path):
    _write_c_fixture(tmp_path)
    (tmp_path / "host" / "test_defaults.c").write_text(
        '#include "gcu/defaults.h"\nint main(void) { return 0; }\n',
        encoding="utf-8",
    )
    report = run_product_path_check(tmp_path)
    assert not report.ok
