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


def test_env_print_missing_is_honest(tmp_path: Path, monkeypatch):
    # Pin home so a real ~/.espressif on the dev machine cannot leak in (#87).
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    missing = tmp_path / "nope.json"
    lines = env_print_block(env={}, eim_json=missing, shell="bash")
    assert any("No IDF" in ln for ln in lines)


def test_which_under_prefers_eim_layout_not_full_tree_scan(tmp_path: Path, monkeypatch):
    """CR: do not recursive-** the whole tools tree first (#79 review)."""
    tools = tmp_path / "tools"
    # Deep noise that would be expensive to walk first
    deep = tools / "noise" / "a" / "b" / "c"
    deep.mkdir(parents=True)
    (deep / "cmake.exe").write_text("nope", encoding="utf-8")
    # Canonical EIM layout
    cmake_bin = tools / "cmake" / "3.30.2" / "bin"
    cmake_bin.mkdir(parents=True)
    good = cmake_bin / "cmake.exe"
    good.write_text("ok", encoding="utf-8")

    calls: list[str] = []
    real_glob = Path.glob

    def tracking_glob(self, pattern):
        calls.append(str(pattern))
        return real_glob(self, pattern)

    monkeypatch.setattr(Path, "glob", tracking_glob)
    monkeypatch.setattr("silico.c_toolchain.shutil.which", lambda _n: None)

    from silico.c_toolchain import _which_under

    found = _which_under(tools, "cmake")
    assert found is not None
    assert found.replace("\\", "/").endswith("cmake/3.30.2/bin/cmake.exe")
    # First search patterns should be narrow (cmake/<ver>/...), not leading **
    assert calls, "expected glob calls"
    assert not calls[0].startswith("**"), f"first pattern too broad: {calls[0]}"


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


# --- macOS/Linux idf_tools.py catalog: ~/.espressif/idf-env.json (#87) ---


def _sample_idf_env() -> dict:
    """Real idf_tools.py schema: idfInstalled is a dict keyed by install id."""
    return {
        "idfInstalled": {
            "/Users/dev/esp/esp-idf-v5.3.2-v5.3": {
                "version": "5.3",
                "path": "/Users/dev/esp/esp-idf-v5.3.2",
                "features": ["core"],
                "targets": ["esp32"],
            }
        }
    }


def _write_idf_env_tree(tmp_path: Path) -> tuple[Path, Path]:
    """Materialize a fake ~/.espressif + IDF tree; returns (idf_env_json, idf_path)."""
    espressif = tmp_path / ".espressif"
    espressif.mkdir()
    idf = tmp_path / "esp" / "esp-idf-v5.3.2"
    (idf / "tools").mkdir(parents=True)
    (idf / "export.sh").write_text("# export\n", encoding="utf-8")
    (idf / "tools" / "idf.py").write_text("# idf.py\n", encoding="utf-8")
    py_env = espressif / "python_env" / "idf5.3_py3.12_env" / "bin"
    py_env.mkdir(parents=True)
    (py_env / "python").write_text("", encoding="utf-8")
    body = {
        "idfInstalled": {
            "id-1": {"version": "5.3", "path": str(idf), "targets": ["esp32"]}
        }
    }
    catalog = espressif / "idf-env.json"
    catalog.write_text(json.dumps(body), encoding="utf-8")
    return catalog, idf


def test_parse_idf_env_json_dict_schema(tmp_path: Path):
    from silico.c_toolchain import parse_idf_env_json

    catalog, idf = _write_idf_env_tree(tmp_path)
    data = json.loads(catalog.read_text(encoding="utf-8"))
    installs, selected_id = parse_idf_env_json(data, espressif_root=catalog.parent)
    assert len(installs) == 1
    inst = installs[0]
    assert inst.path == str(idf)
    assert "5.3" in inst.name
    # export.sh is the bash activation for idf_tools installs
    assert inst.activation_script.endswith("export.sh")
    # python env under ~/.espressif/python_env resolved when it matches the version
    assert "idf5.3_py3.12_env" in inst.python


def test_parse_idf_env_json_ignores_junk():
    from silico.c_toolchain import parse_idf_env_json

    installs, selected_id = parse_idf_env_json(
        {"idfInstalled": {"x": "not-a-dict", "y": {"version": "5.1"}}},
        espressif_root=None,
    )
    assert installs == []
    assert selected_id is None


def test_find_idf_env_json_home_and_tools_path(tmp_path: Path, monkeypatch):
    from silico.c_toolchain import find_idf_env_json

    catalog, _idf = _write_idf_env_tree(tmp_path)
    # via IDF_TOOLS_PATH
    found = find_idf_env_json(env={"IDF_TOOLS_PATH": str(catalog.parent)})
    assert found == catalog
    # via home (~/.espressif)
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    found = find_idf_env_json(env={})
    assert found == catalog


def test_discover_falls_back_to_idf_env_json(tmp_path: Path, monkeypatch):
    """No EIM catalog + no $IDF_PATH: an existing ~/.espressif install must be found."""
    catalog, idf = _write_idf_env_tree(tmp_path)
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    monkeypatch.setattr("silico.c_toolchain.shutil.which", lambda _n: None)
    r = discover_c_toolchain(env={}, eim_json=tmp_path / "no-eim.json")
    assert r.ok
    assert r.selected is not None
    assert r.selected.path == str(idf)
    assert r.idf_py is not None and r.idf_py.endswith("idf.py")


def test_doctor_lines_surface_idf_env_install(tmp_path: Path, monkeypatch):
    catalog, idf = _write_idf_env_tree(tmp_path)
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    monkeypatch.setattr("silico.c_toolchain.shutil.which", lambda _n: None)
    lines = doctor_c_toolchain_lines(env={}, eim_json=tmp_path / "no-eim.json")
    joined = "\n".join(lines)
    assert str(idf) in joined
    # actionable bash activation, not a bare "not found"
    assert "export.sh" in joined
    assert "WARN: no ESP-IDF install resolved" not in joined


def test_doctor_missing_message_mentions_idf_env(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    lines = doctor_c_toolchain_lines(env={}, eim_json=tmp_path / "no-eim.json")
    joined = "\n".join(lines)
    assert "idf-env.json" in joined


def test_env_print_bash_sources_export_sh(tmp_path: Path, monkeypatch):
    catalog, idf = _write_idf_env_tree(tmp_path)
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    lines = env_print_block(env={}, eim_json=tmp_path / "no-eim.json", shell="bash")
    joined = "\n".join(lines)
    assert f'export IDF_PATH="{idf}"' in joined
    assert "export.sh" in joined

def test_python_env_prefers_newest_python_not_lexicographic(tmp_path: Path):
    # Review finding (PR #88): sorted() is lexicographic, so py3.9 sorts
    # AFTER py3.12 and used to win. This is the exact macOS failure mode:
    # a bad system-3.9 env installed first, then a good 3.12 reinstall.
    from silico.c_toolchain import _python_env_for

    espressif = tmp_path / ".espressif"
    for name in ("idf5.3_py3.9_env", "idf5.3_py3.12_env"):
        b = espressif / "python_env" / name / "bin"
        b.mkdir(parents=True)
        (b / "python").write_text("", encoding="utf-8")
    assert "py3.12" in _python_env_for(espressif, "5.3")


def test_python_env_fallback_prefers_newest_idf(tmp_path: Path):
    from silico.c_toolchain import _python_env_for

    espressif = tmp_path / ".espressif"
    for name in ("idf5.9_py3.12_env", "idf5.10_py3.12_env"):
        b = espressif / "python_env" / name / "bin"
        b.mkdir(parents=True)
        (b / "python").write_text("", encoding="utf-8")
    # No env matches version 6.0 -> fall back to the newest IDF env, which
    # is 5.10 (numeric), not 5.9 (lexicographic winner).
    assert "idf5.10_" in _python_env_for(espressif, "6.0")
