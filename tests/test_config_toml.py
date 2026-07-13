from pathlib import Path

from silico.config_toml import read_deploy_core
from silico.deploy import (
    DeployResult,
    device_verify_import_snippet,
    resolve_deploy_files,
)


def test_read_deploy_core(tmp_path: Path, monkeypatch):
    (tmp_path / "silico.toml").write_text(
        '[deploy]\ncore = ["firmware/version.py", "firmware/main.py"]\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    assert read_deploy_core() == ["firmware/version.py", "firmware/main.py"]


def test_read_deploy_core_ignores_comments(tmp_path: Path, monkeypatch):
    (tmp_path / "silico.toml").write_text(
        """
[deploy]
core = [
  "firmware/version.py",
  # "firmware/legacy.py",
  "firmware/main.py",
]
""",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    assert read_deploy_core() == ["firmware/version.py", "firmware/main.py"]


def test_resolve_uses_manifest(tmp_path: Path, monkeypatch):
    fw = tmp_path / "firmware"
    fw.mkdir()
    (fw / "version.py").write_text("x=1\n", encoding="utf-8")
    (fw / "main.py").write_text("y=1\n", encoding="utf-8")
    (tmp_path / "silico.toml").write_text(
        '[deploy]\ncore = ["firmware/version.py", "firmware/main.py"]\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    got = resolve_deploy_files(None, root=tmp_path)
    assert not isinstance(got, DeployResult)
    assert len(got) == 2
    assert got[0].name == "version.py"


def test_resolve_missing_manifest_fails(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    got = resolve_deploy_files(None, root=tmp_path)
    assert isinstance(got, DeployResult)
    assert not got.ok


def test_verify_import_main_uses_compile_not_import():
    code, mode = device_verify_import_snippet("main")
    assert mode == "compile"
    assert "import main" not in code
    assert "compile(" in code
    assert "main.py" in code


def test_verify_import_version_uses_import():
    code, mode = device_verify_import_snippet("version")
    assert mode == "import"
    assert "import version" in code
