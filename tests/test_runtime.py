from pathlib import Path

from silico.backend import BACKEND_IDF, BACKEND_INVALID, BACKEND_MPY, backend_kind
from silico.runtime import LANG_C, LANG_MICROPYTHON, resolve_runtime


def test_default_language_is_micropython(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "silico.toml").write_text("[product]\nname = 'X'\n", encoding="utf-8")
    cfg = resolve_runtime(tmp_path)
    assert cfg.language == LANG_MICROPYTHON
    assert cfg.deploy_mode == "file-copy"
    assert cfg.ok
    assert backend_kind(cfg) == BACKEND_MPY


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
    assert cfg.ok
    assert cfg.errors == ()
    assert backend_kind(cfg) == BACKEND_IDF


def test_missing_chip_is_warning_not_fail(tmp_path: Path):
    (tmp_path / "silico.toml").write_text(
        """
[runtime]
language = "c"
""",
        encoding="utf-8",
    )
    cfg = resolve_runtime(tmp_path)
    assert cfg.ok
    assert cfg.errors == ()
    assert any("chip" in w.lower() for w in cfg.warnings)
    assert cfg.chip == "esp32"
    assert backend_kind(cfg) == BACKEND_IDF


def test_unknown_language_fails_closed(tmp_path: Path):
    (tmp_path / "silico.toml").write_text(
        '[runtime]\nlanguage = "rust"\n',
        encoding="utf-8",
    )
    cfg = resolve_runtime(tmp_path)
    assert not cfg.ok
    assert any("unknown" in e.lower() for e in cfg.errors)
    assert not cfg.is_micropython
    assert not cfg.is_c
    assert backend_kind(cfg) == BACKEND_INVALID


def test_cpp_not_a_peer_language(tmp_path: Path):
    (tmp_path / "silico.toml").write_text(
        '[runtime]\nlanguage = "cpp"\n',
        encoding="utf-8",
    )
    cfg = resolve_runtime(tmp_path)
    assert not cfg.ok
    assert any("unknown" in e.lower() for e in cfg.errors)
    assert backend_kind(cfg) == BACKEND_INVALID


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
    assert not cfg.ok
    assert any("language=c" in e for e in cfg.errors)
