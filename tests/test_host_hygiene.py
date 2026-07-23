from pathlib import Path

from silico.config_toml import read_hal_allow_machine
from silico.host_hygiene import run_hygiene, scan_machine_imports
from silico.scaffold import scaffold


def test_scan_machine_import_from():
    src = "def f():\n    from machine import Pin\n"
    hits = scan_machine_imports(src)
    assert len(hits) == 1
    assert hits[0][0] == 2


def test_scan_no_machine():
    assert scan_machine_imports("import sys\nx = 1\n") == []


def test_read_hal_allow_machine(tmp_path: Path):
    (tmp_path / "silico.toml").write_text(
        '[hal]\nallow_machine = ["hal_board", "firmware/other.py"]\n',
        encoding="utf-8",
    )
    assert read_hal_allow_machine(tmp_path) == ["hal_board", "other"]


def test_plate_hygiene_passes(tmp_path: Path):
    dest = tmp_path / "gcu"
    scaffold(dest)
    report = run_hygiene(dest)
    assert report.ok, "\n".join(report.lines)


def test_hygiene_fails_when_domain_imports_machine(tmp_path: Path):
    dest = tmp_path / "gcu"
    scaffold(dest)
    # Inject illegal machine use into main (not allowlisted).
    main = dest / "firmware" / "main.py"
    text = main.read_text(encoding="utf-8")
    main.write_text("import machine\n" + text, encoding="utf-8")
    report = run_hygiene(dest)
    assert not report.ok
    assert any("allow_machine" in line or "machine" in line for line in report.lines)


def test_cli_gate_on_plate(tmp_path: Path, monkeypatch):
    from silico.cli import main

    dest = tmp_path / "gcu"
    scaffold(dest)
    monkeypatch.chdir(dest)
    assert main(["gate"]) == 0

def test_hygiene_skips_binary_deploy_assets(tmp_path: Path):
    (tmp_path / "firmware").mkdir()
    (tmp_path / "firmware" / "version.py").write_text(
        'FW_NAME = "X"\nFW_VERSION = "0.0.1"\n', encoding="utf-8"
    )
    (tmp_path / "firmware" / "main.py").write_text(
        "def init(hal=None):\n    return {}\n\ndef tick(state):\n    return state\n",
        encoding="utf-8",
    )
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "riff.u8.raw").write_bytes(bytes([128, 200, 50, 0]))
    (tmp_path / "silico.toml").write_text(
        """
[hal]
allow_machine = []
[deploy]
core = [
  "firmware/version.py",
  "firmware/main.py",
  "assets/riff.u8.raw",
]
""",
        encoding="utf-8",
    )
    report = run_hygiene(tmp_path)
    assert report.ok, "\n".join(report.lines)
    assert any("non-Python deploy asset" in line for line in report.lines)
