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
    from silico.deploy_types import DeployPlan, DeployResult

    planned = plan_idf_deploy(port="COM7", root=root)
    assert isinstance(planned, DeployPlan)
    assert planned.kind == "idf"
    assert planned.build_cmd and planned.flash_cmd
    assert not isinstance(planned, DeployResult)
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

    live: list[str] = []
    r = deploy_idf(
        port="COM7", yes=True, verify=False, root=root, run_fn=run_fn, on_progress=live.append
    )
    assert r.ok, r.lines
    assert len(calls) == 2
    assert any("build" in c for c in calls[0])
    assert any("flash" in c for c in calls[1])
    # CR: IDF path must stream progress via on_progress (not silent under CLI --yes)
    assert live == r.lines
    assert any("PROGRESS" in x or "Building" in x or "build" in x.lower() for x in live)
    assert any("OK: build" in x for x in live)
    assert any("OK: flash" in x for x in live)


def test_deploy_idf_yes_writes_data_partition(tmp_path: Path, monkeypatch):
    """[[deploy.data]] must esptool write_flash only after --yes (shipped deploy_idf path)."""
    root = _c_root(tmp_path)
    import silico.deploy_idf as m
    import silico.ports as ports

    csv = """\
# Name, Type, SubType, Offset, Size, Flags
storage, data, spiffs, 0x210000, 0xF0000,
"""
    (root / "firmware" / "partitions.csv").write_text(csv, encoding="utf-8")
    assets = root / "assets"
    assets.mkdir()
    blob = assets / "song.raw"
    blob.write_bytes(b"\xab" * 64)
    toml = (root / "silico.toml").read_text(encoding="utf-8")
    (root / "silico.toml").write_text(
        toml
        + """
[[deploy.data]]
name = "song"
file = "assets/song.raw"
partition = "storage"
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        ports,
        "list_scored_ports",
        lambda: [PortInfo("COM7", 0x1A86, 0x55D4, "CH9102", "m", 55, "ESP")],
    )
    monkeypatch.setattr(ports, "port_is_listed", lambda d: True)
    monkeypatch.setattr(m, "idf_py_available", lambda: True)
    monkeypatch.setattr(m, "esptool_available", lambda: True)

    class Fake:
        def __init__(self, code=0):
            self.returncode = code
            self.stdout = "ok"
            self.stderr = ""

    calls: list[list[str]] = []

    def run_fn(cmd, *, cwd):
        calls.append(list(cmd))
        return Fake(0)

    # Without --yes: no esptool, no build
    aborted = deploy_idf(port="COM7", yes=False, verify=False, root=root, run_fn=run_fn)
    assert not aborted.ok
    assert calls == []
    assert any("Data partitions" in x or "0x210000" in x for x in aborted.lines)

    # With --yes: build + flash + esptool write_flash @ partition offset
    r = deploy_idf(port="COM7", yes=True, verify=False, root=root, run_fn=run_fn)
    assert r.ok, r.lines
    assert len(calls) >= 3
    assert any("build" in c for c in calls[0])
    assert any("flash" in c for c in calls[1])
    data_cmds = [c for c in calls if any("write_flash" in str(x) for x in c)]
    assert data_cmds, f"expected esptool write_flash in calls={calls!r}"
    flat = " ".join(str(x) for x in data_cmds[0])
    assert "0x210000" in flat
    assert "song.raw" in flat
    assert any("OK: data" in x and "song" in x for x in r.lines)


def test_deploy_dispatch_idf_passes_on_progress(tmp_path: Path, monkeypatch):
    """CLI deploy --yes with language=c must forward on_progress (not silent)."""
    from silico import deploy as deploy_mod
    from silico.deploy import deploy
    from silico.deploy_types import DeployResult
    from silico.progress import ProgressLog

    root = _c_root(tmp_path)
    monkeypatch.chdir(root)
    import silico.ports as ports

    monkeypatch.setattr(
        ports,
        "list_scored_ports",
        lambda: [PortInfo("COM7", 0x1A86, 0x55D4, "CH9102", "m", 55, "ESP")],
    )
    monkeypatch.setattr(ports, "port_is_listed", lambda d: True)

    seen: dict = {}

    def fake_idf(**kwargs):
        seen["on_progress"] = kwargs.get("on_progress")
        log = ProgressLog(kwargs.get("on_progress"))
        log("PROGRESS [idf-build] fake")
        log("OK: build")
        log("OK: flash")
        return DeployResult(True, log.lines)

    monkeypatch.setattr(deploy_mod, "deploy_idf", fake_idf)
    live: list[str] = []
    cb = live.append
    r = deploy(None, port="COM7", yes=True, root=root, on_progress=cb)
    assert r.ok, r.lines
    assert seen.get("on_progress") is cb
    assert live
    assert live == r.lines


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


def test_idf_invocation_uses_sys_executable(monkeypatch, tmp_path: Path):
    import silico.deploy_idf as m

    monkeypatch.delenv("IDF_PATH", raising=False)
    monkeypatch.setattr(m.shutil, "which", lambda name: None)
    monkeypatch.setenv("IDF_PATH", str(tmp_path))
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / "idf.py").write_text("# idf\n", encoding="utf-8")
    inv = m._idf_py_invocation()
    assert inv[0].endswith("python.exe") or "python" in inv[0].lower() or inv[0]
    import sys

    assert inv[0] == sys.executable
    assert inv[1].endswith("idf.py")
