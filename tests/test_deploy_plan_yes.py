"""Deploy plan wording: refuse line only without --yes (tig/silico#84)."""

from pathlib import Path

from silico.deploy import plan_deploy
from silico.deploy_idf import plan_idf_deploy
from silico.ports import PortInfo


def _fake_port(device: str = "COM7") -> PortInfo:
    return PortInfo(
        device=device,
        vid=0x1A86,
        pid=0x55D4,
        description="CH9102",
        manufacturer="wch",
        score=80,
        label="esp",
    )


def test_mpy_plan_refuses_without_yes(tmp_path: Path, monkeypatch):
    from silico import deploy as deploy_mod

    f = tmp_path / "main.py"
    f.write_text("print(1)\n", encoding="utf-8")
    monkeypatch.setattr(deploy_mod, "mpremote_available", lambda: True)
    monkeypatch.setattr(deploy_mod, "pick_best_port", lambda explicit=None: _fake_port())
    monkeypatch.setattr(deploy_mod, "port_is_listed", lambda _d: True)
    planned = plan_deploy([f], port="COM7", root=tmp_path, yes=False)
    text = "\n".join(planned.lines)
    assert "Refusing to write without explicit confirmation (--yes)." in text
    assert "Write confirmed (--yes)" not in text


def test_mpy_plan_confirmed_with_yes(tmp_path: Path, monkeypatch):
    from silico import deploy as deploy_mod

    f = tmp_path / "main.py"
    f.write_text("print(1)\n", encoding="utf-8")
    monkeypatch.setattr(deploy_mod, "mpremote_available", lambda: True)
    monkeypatch.setattr(deploy_mod, "pick_best_port", lambda explicit=None: _fake_port())
    monkeypatch.setattr(deploy_mod, "port_is_listed", lambda _d: True)
    planned = plan_deploy([f], port="COM7", root=tmp_path, yes=True)
    text = "\n".join(planned.lines)
    assert "Refusing to write without explicit confirmation (--yes)." not in text
    assert "Write confirmed (--yes)" in text


def test_idf_plan_refuses_without_yes(tmp_path: Path, monkeypatch):
    from silico import deploy_idf as idf

    (tmp_path / "silico.toml").write_text(
        '[runtime]\nlanguage = "c"\nchip = "esp32"\n[deploy]\nproject = "firmware"\n',
        encoding="utf-8",
    )
    (tmp_path / "firmware").mkdir()
    monkeypatch.setattr(idf, "pick_best_port", lambda explicit=None: _fake_port())
    monkeypatch.setattr(idf, "port_is_listed", lambda _d: True)
    monkeypatch.setattr(idf, "idf_py_available", lambda: True)
    planned = plan_idf_deploy(port="COM7", root=tmp_path, yes=False)
    text = "\n".join(planned.lines)
    assert "Refusing to write without explicit confirmation (--yes)." in text


def test_idf_plan_confirmed_with_yes(tmp_path: Path, monkeypatch):
    from silico import deploy_idf as idf

    (tmp_path / "silico.toml").write_text(
        '[runtime]\nlanguage = "c"\nchip = "esp32"\n[deploy]\nproject = "firmware"\n',
        encoding="utf-8",
    )
    (tmp_path / "firmware").mkdir()
    monkeypatch.setattr(idf, "pick_best_port", lambda explicit=None: _fake_port())
    monkeypatch.setattr(idf, "port_is_listed", lambda _d: True)
    monkeypatch.setattr(idf, "idf_py_available", lambda: True)
    planned = plan_idf_deploy(port="COM7", root=tmp_path, yes=True)
    text = "\n".join(planned.lines)
    assert "Refusing to write without explicit confirmation (--yes)." not in text
    assert "Write confirmed (--yes)" in text
