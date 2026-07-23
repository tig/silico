"""C/EIM toolchain discovery (#79) — pure parse + path resolution, no real EIM required."""

from __future__ import annotations

import json
from pathlib import Path

from silico.c_toolchain import (
    discover_c_toolchain,
    doctor_c_toolchain_lines,
    env_print_block,
    find_eim_json,
    parse_eim_idf_json,
    select_install,
)


def _sample_eim() -> dict:
    return {
        "gitPath": "C:\\Program Files\\Git\\cmd\\git.exe",
        "idfInstalled": [
            {
                "activationScript": "C:\\Espressif\\tools\\Microsoft.v5.3.2.PowerShell_profile.ps1",
                "id": "esp-idf-aaa",
                "idfToolsPath": "C:\\Espressif\\tools",
                "name": "v5.3.2",
                "path": "C:\\esp\\v5.3.2\\esp-idf",
                "python": "C:\\Espressif\\tools\\python\\v5.3.2\\venv\\Scripts\\python.exe",
            },
            {
                "activationScript": "C:\\Espressif\\tools\\other.ps1",
                "id": "esp-idf-bbb",
                "idfToolsPath": "C:\\Espressif\\tools",
                "name": "v5.1.0",
                "path": "C:\\esp\\v5.1.0\\esp-idf",
                "python": "C:\\Espressif\\tools\\python\\v5.1.0\\venv\\Scripts\\python.exe",
            },
        ],
        "idfSelectedId": "esp-idf-aaa",
        "version": "2.0",
    }


def test_parse_eim_idf_json_selects_named_install():
    installs, selected_id = parse_eim_idf_json(_sample_eim())
    assert len(installs) == 2
    assert selected_id == "esp-idf-aaa"
    chosen = select_install(installs, selected_id)
    assert chosen is not None
    assert chosen.name == "v5.3.2"
    assert chosen.path.endswith("esp-idf")
    assert "PowerShell_profile.ps1" in chosen.activation_script


def test_find_eim_json_from_extra(tmp_path: Path):
    catalog = tmp_path / "eim_idf.json"
    catalog.write_text(json.dumps(_sample_eim()), encoding="utf-8")
    found = find_eim_json(env={}, extra=[catalog])
    assert found == catalog


def test_discover_reads_fixture_json(tmp_path: Path):
    catalog = tmp_path / "eim_idf.json"
    catalog.write_text(json.dumps(_sample_eim()), encoding="utf-8")
    r = discover_c_toolchain(env={}, eim_json=catalog)
    assert r.selected is not None
    assert r.selected.name == "v5.3.2"
    assert r.eim_json == catalog


def test_doctor_lines_include_activation(tmp_path: Path):
    catalog = tmp_path / "eim_idf.json"
    catalog.write_text(json.dumps(_sample_eim()), encoding="utf-8")
    lines = doctor_c_toolchain_lines(env={}, eim_json=catalog)
    joined = "\n".join(lines)
    assert "v5.3.2" in joined
    assert "activation" in joined.lower()
    assert "PowerShell_profile.ps1" in joined


def test_env_print_powershell_block(tmp_path: Path):
    catalog = tmp_path / "eim_idf.json"
    catalog.write_text(json.dumps(_sample_eim()), encoding="utf-8")
    lines = env_print_block(env={}, eim_json=catalog, shell="powershell")
    joined = "\n".join(lines)
    assert "$env:IDF_PATH" in joined
    assert "C:\\esp\\v5.3.2\\esp-idf" in joined
    assert "PowerShell_profile.ps1" in joined


def test_env_print_missing_is_honest(tmp_path: Path):
    missing = tmp_path / "nope.json"
    lines = env_print_block(env={}, eim_json=missing, shell="bash")
    assert any("No IDF" in ln for ln in lines)


def test_cli_env_print(tmp_path: Path, monkeypatch, capsys):
    from silico.cli import main
    import silico.c_toolchain as ct

    catalog = tmp_path / "eim_idf.json"
    catalog.write_text(json.dumps(_sample_eim()), encoding="utf-8")
    real_discover = ct.discover_c_toolchain

    def _discover(**kwargs):
        kwargs["eim_json"] = catalog
        return real_discover(**kwargs)

    monkeypatch.setattr(ct, "discover_c_toolchain", _discover)
    rc = main(["env", "--print", "--shell", "powershell"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "IDF_PATH" in out
    assert "v5.3.2" in out or "esp-idf" in out
