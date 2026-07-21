from pathlib import Path

from silico.deploy import plan_deploy
from silico.deploy_idf import deploy_idf, plan_idf_deploy
from silico.ports import PortInfo


def _c_root(tmp_path: Path) -> Path:
    (tmp_path / "silico.toml").write_text(
        """
[product]
fw_name = "GCU"
fw_version = "0.0.1"
[runtime]
language = "c"
chip = "esp32"
[deploy]
mode = "idf-flash"
project = "firmware"
""",
        encoding="utf-8",
    )
    (tmp_path / "firmware").mkdir()
    (tmp_path / "firmware" / "CMakeLists.txt").write_text("# idf\n", encoding="utf-8")
    return tmp_path


def test_plan_idf_requires_port(tmp_path: Path):
    root = _c_root(tmp_path)
    r = plan_idf_deploy(port=None, root=root)
    assert getattr(r, "ok", True) is False
    assert any("explicit --port" in x for x in r.lines)


def test_plan_idf_shows_overwrite_image(tmp_path: Path, monkeypatch):
    root = _c_root(tmp_path)
    import silico.deploy_idf as m
    import silico.ports as ports

    monkeypatch.setattr(
        ports,
        "list_scored_ports",
        lambda: [PortInfo("COM7", 0x1A86, 0x55D4, "CH9102", "m", 55, "ESP")],
    )
    monkeypatch.setattr(ports, "port_is_listed", lambda d: d == "COM7")
    from silico.deploy_idf import IdfDeployPlan, IdfDeployResult

    planned = plan_idf_deploy(port="COM7", root=root)
    assert isinstance(planned, IdfDeployPlan)
    assert not isinstance(planned, IdfDeployResult)
    text = "\n".join(planned.lines)
    assert "OVERWRITE the entire application image" in text
    assert "idf.py" in text or "build" in text


def test_dispatch_plan_deploy_c(tmp_path: Path, monkeypatch):
    root = _c_root(tmp_path)
    import silico.ports as ports

    monkeypatch.chdir(root)
    monkeypatch.setattr(
        ports,
        "list_scored_ports",
        lambda: [PortInfo("COM7", 0x1A86, 0x55D4, "CH9102", "m", 55, "ESP")],
    )
    monkeypatch.setattr(ports, "port_is_listed", lambda d: d.upper() == "COM7")
    planned = plan_deploy(None, port="COM7", root=root)
    assert hasattr(planned, "lines")
    assert any("application image" in x for x in planned.lines)


def test_deploy_idf_aborts_without_yes(tmp_path: Path, monkeypatch):
    root = _c_root(tmp_path)
    import silico.ports as ports

    monkeypatch.setattr(
        ports,
        "list_scored_ports",
        lambda: [PortInfo("COM7", 0x1A86, 0x55D4, "CH9102", "m", 55, "ESP")],
    )
    monkeypatch.setattr(ports, "port_is_listed", lambda d: True)
    r = deploy_idf(port="COM7", yes=False, root=root)
    assert not r.ok
    assert any("ABORTED" in x for x in r.lines)


def test_deploy_idf_mock_build_flash(tmp_path: Path, monkeypatch):
    root = _c_root(tmp_path)
    import silico.deploy_idf as m
    import silico.ports as ports

    monkeypatch.setattr(
        ports,
        "list_scored_ports",
        lambda: [PortInfo("COM7", 0x1A86, 0x55D4, "CH9102", "m", 55, "ESP")],
    )
    monkeypatch.setattr(ports, "port_is_listed", lambda d: True)
    monkeypatch.setattr(m, "idf_py_available", lambda: True)

    class Fake:
        def __init__(self, code=0):
            self.returncode = code
            self.stdout = "ok"
            self.stderr = ""

    calls = []

    def run_fn(cmd, *, cwd):
        calls.append(cmd)
        return Fake(0)

    r = deploy_idf(port="COM7", yes=True, verify=False, root=root, run_fn=run_fn)
    assert r.ok, r.lines
    assert len(calls) == 2
    assert any("build" in c for c in calls[0])
    assert any("flash" in c for c in calls[1])


def test_mpy_flags_rejected_on_c(tmp_path: Path, monkeypatch):
    from silico.deploy import deploy

    root = _c_root(tmp_path)
    monkeypatch.chdir(root)
    import silico.ports as ports

    monkeypatch.setattr(ports, "port_is_listed", lambda d: True)
    monkeypatch.setattr(
        ports,
        "list_scored_ports",
        lambda: [PortInfo("COM7", 0x1A86, 0x55D4, "CH9102", "m", 55, "ESP")],
    )
    r = deploy(None, port="COM7", yes=True, verify_import="main", root=root)
    assert not r.ok
    assert any("MicroPython-only" in x for x in r.lines)
