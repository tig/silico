from pathlib import Path

from silico.workspace import detect_workspace


def test_detect_gcu_spec_only(tmp_path: Path):
    (tmp_path / "spec.md").write_text("# Product\n", encoding="utf-8")
    ws = detect_workspace(tmp_path)
    assert ws.mode == "gcu"
    assert any("spec.md" in r for r in ws.reasons)


def test_detect_silico_package(tmp_path: Path):
    (tmp_path / "silico" / "plates").mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text('name = "tig-silico"\n', encoding="utf-8")
    ws = detect_workspace(tmp_path)
    assert ws.mode == "silico-package"


def test_detect_unknown(tmp_path: Path):
    ws = detect_workspace(tmp_path)
    assert ws.mode == "unknown"
