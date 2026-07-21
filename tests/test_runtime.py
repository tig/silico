from pathlib import Path

from silico.runtime import LANG_C, LANG_MICROPYTHON, resolve_runtime


def test_default_language_is_micropython(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "silico.toml").write_text("[product]\nname = 'X'\n", encoding="utf-8")
    cfg = resolve_runtime(tmp_path)
    assert cfg.language == LANG_MICROPYTHON
    assert cfg.deploy_mode == "file-copy"
    assert cfg.ok or not any(e.startswith("FAIL:") for e in cfg.errors)


def test_language_c_defaults_toolchain_and_mode(tmp_path: Path):
    (tmp_path / "silico.toml").write_text(
        """
[runtime]
language = "c"
chip = "esp32"
[deploy]
project = "firmware"
""",
        encoding="utf-8",
    )
    cfg = resolve_runtime(tmp_path)
    assert cfg.language == LANG_C
    assert cfg.toolchain == "esp-idf"
    assert cfg.deploy_mode == "idf-flash"
    assert cfg.project == "firmware"
    assert cfg.chip == "esp32"
    assert not any(e.startswith("FAIL:") for e in cfg.errors)


def test_unknown_language_fails(tmp_path: Path):
    (tmp_path / "silico.toml").write_text(
        '[runtime]\nlanguage = "rust"\n',
        encoding="utf-8",
    )
    cfg = resolve_runtime(tmp_path)
    assert any("unknown" in e.lower() for e in cfg.errors)


def test_cpp_not_a_peer_language(tmp_path: Path):
    (tmp_path / "silico.toml").write_text(
        '[runtime]\nlanguage = "cpp"\n',
        encoding="utf-8",
    )
    cfg = resolve_runtime(tmp_path)
    assert any("unknown" in e.lower() for e in cfg.errors)


def test_idf_toolchain_requires_c(tmp_path: Path):
    (tmp_path / "silico.toml").write_text(
        """
[runtime]
language = "micropython"
toolchain = "esp-idf"
""",
        encoding="utf-8",
    )
    cfg = resolve_runtime(tmp_path)
    assert any("language=c" in e for e in cfg.errors)
