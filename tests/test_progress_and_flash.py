"""Operator-visible progress for deploy / pull / first-flash."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from silico import deploy as deploy_mod
from silico.esptool_util import copy_with_progress
from silico.first_flash import FirstFlashPlan, FirstFlashResult, first_flash, plan_first_flash
from silico.ports import PortInfo
from silico.progress import emit, file_step, format_bytes, stage_header
from silico.pull_device import pull_device


def test_format_bytes():
    assert format_bytes(500) == "500 B"
    assert "KiB" in format_bytes(2048)
    assert "MiB" in format_bytes(2 * 1024 * 1024)


def test_file_step_shape():
    s = file_step(stage="write", index=2, total=7, name="main.py", size=1200, verb="Writing")
    assert s.startswith("PROGRESS [write] 2/7 main.py")
    assert "Writing" in s


def test_emit_streams_and_records():
    lines: list[str] = []
    live: list[str] = []
    emit(lines, "hello", on_progress=live.append)
    assert lines == ["hello"]
    assert live == ["hello"]


def test_deploy_plan_includes_sizes_and_progress_hint(tmp_path: Path, monkeypatch):
    f = tmp_path / "version.py"
    f.write_text("FW_NAME='X'\nFW_VERSION='0.0.1'\n", encoding="utf-8")
    monkeypatch.setattr(deploy_mod, "mpremote_available", lambda: True)
    monkeypatch.setattr(
        deploy_mod,
        "pick_best_port",
        lambda explicit=None: PortInfo(
            device="COM9",
            vid=0x2E8A,
            pid=0x0005,
            description="test",
            manufacturer="test",
            score=100,
            label="test board",
        ),
    )
    monkeypatch.setattr(deploy_mod, "port_is_listed", lambda _d: True)
    plan = deploy_mod.plan_deploy([f], port="COM9")
    assert not isinstance(plan, deploy_mod.DeployResult)
    text = "\n".join(plan.lines)
    assert "PROGRESS [plan]" in text
    assert "Total payload:" in text
    assert "version.py" in text
    assert "PROGRESS [write]" in text


def test_deploy_yes_emits_live_progress(tmp_path: Path, monkeypatch):
    f = tmp_path / "version.py"
    f.write_text("FW_NAME='X'\nFW_VERSION='0.0.1'\n", encoding="utf-8")
    monkeypatch.setattr(deploy_mod, "mpremote_available", lambda: True)
    monkeypatch.setattr(
        deploy_mod,
        "pick_best_port",
        lambda explicit=None: PortInfo(
            device="COM9",
            vid=0x2E8A,
            pid=0x0005,
            description="test",
            manufacturer="test",
            score=100,
            label="test board",
        ),
    )
    monkeypatch.setattr(deploy_mod, "port_is_listed", lambda _d: True)

    class R:
        returncode = 0
        stdout = ""
        stderr = ""

    monkeypatch.setattr(deploy_mod, "cp_to_device", lambda *a, **k: R())
    live: list[str] = []
    result = deploy_mod.deploy([f], port="COM9", yes=True, on_progress=live.append)
    assert result.ok
    joined = "\n".join(live)
    assert "PROGRESS [write]" in joined
    assert "OK: wrote :version.py" in joined
    assert "PROGRESS [done]" in joined


def test_pull_progress(tmp_path: Path, monkeypatch):
    from silico import pull_device as pull_mod

    monkeypatch.setattr(pull_mod, "mpremote_available", lambda: True)
    monkeypatch.setattr(
        pull_mod,
        "pick_best_port",
        lambda explicit=None: PortInfo(
            device="COM9",
            vid=0x2E8A,
            pid=0x0005,
            description="test",
            manufacturer="test",
            score=100,
            label="test board",
        ),
    )
    monkeypatch.setattr(pull_mod, "port_is_listed", lambda _d: True)

    class Ls:
        returncode = 0
        stdout = "   10 main.py\n   20 version.py\n"
        stderr = ""

    class Cp:
        returncode = 0
        stdout = ""
        stderr = ""

    monkeypatch.setattr(pull_mod, "ls_device", lambda _p: Ls())
    monkeypatch.setattr(pull_mod, "run_mpremote", lambda *a, **k: Cp())
    live: list[str] = []
    dest = tmp_path / "backup"
    result = pull_device(dest, port="COM9", on_progress=live.append)
    assert result.ok
    assert any("PROGRESS [pull]" in x for x in live)
    assert any("1/2" in x or "2/2" in x for x in live)


def test_copy_with_progress(tmp_path: Path):
    src = tmp_path / "fw.uf2"
    src.write_bytes(b"x" * 10_000)
    dest = tmp_path / "out" / "fw.uf2"
    live: list[str] = []
    copy_with_progress(src, dest, on_progress=live.append, chunk_size=1024)
    assert dest.is_file()
    assert dest.stat().st_size == 10_000
    assert any("PROGRESS [uf2-copy]" in x for x in live)
    assert any("100%" in x for x in live)


def test_first_flash_plan_esptool(tmp_path: Path, monkeypatch):
    from silico import first_flash as ff

    img = tmp_path / "ESP32.bin"
    img.write_bytes(b"\x00" * 100)
    monkeypatch.setattr(ff, "esptool_available", lambda: True)
    monkeypatch.setattr(
        ff,
        "pick_best_port",
        lambda explicit=None: PortInfo(
            device="COM7",
            vid=1,
            pid=1,
            description="esp",
            manufacturer="t",
            score=80,
            label="esp board",
        ),
    )
    monkeypatch.setattr(ff, "port_is_listed", lambda _d: True)
    plan = plan_first_flash(image=img, port="COM7")
    assert isinstance(plan, FirstFlashPlan)
    text = "\n".join(plan.lines)
    assert "esptool" in text
    assert "COM7" in text
    assert "Refusing without --yes" in text


def test_first_flash_aborts_without_yes(tmp_path: Path, monkeypatch):
    from silico import first_flash as ff

    img = tmp_path / "ESP32.bin"
    img.write_bytes(b"\x00" * 100)
    monkeypatch.setattr(ff, "esptool_available", lambda: True)
    monkeypatch.setattr(
        ff,
        "pick_best_port",
        lambda explicit=None: PortInfo(
            device="COM7",
            vid=1,
            pid=1,
            description="esp",
            manufacturer="t",
            score=80,
            label="esp board",
        ),
    )
    monkeypatch.setattr(ff, "port_is_listed", lambda _d: True)
    live: list[str] = []
    result = first_flash(image=img, port="COM7", yes=False, on_progress=live.append)
    assert not result.ok
    assert any("ABORTED" in x for x in result.lines)


def test_first_flash_esptool_yes_streams(tmp_path: Path, monkeypatch):
    from silico import first_flash as ff

    img = tmp_path / "ESP32.bin"
    img.write_bytes(b"\x00" * 100)
    monkeypatch.setattr(ff, "esptool_available", lambda: True)
    monkeypatch.setattr(
        ff,
        "pick_best_port",
        lambda explicit=None: PortInfo(
            device="COM7",
            vid=1,
            pid=1,
            description="esp",
            manufacturer="t",
            score=80,
            label="esp board",
        ),
    )
    monkeypatch.setattr(ff, "port_is_listed", lambda _d: True)

    calls: list[list[str]] = []

    def fake_esptool(args, on_progress=None, timeout=None):
        calls.append(list(args))
        if on_progress:
            on_progress("PROGRESS [esptool] Writing at 0x00010000... (50 %)")
        return MagicMock(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(ff, "run_esptool_streaming", fake_esptool)
    live: list[str] = []
    result = first_flash(image=img, port="COM7", yes=True, on_progress=live.append)
    assert result.ok
    assert any("erase-flash" in c for c in calls)
    assert any("write-flash" in c for c in calls)
    assert any("PROGRESS [esptool]" in x for x in live)
    assert any("OK: write-flash" in x for x in live)


def test_first_flash_uf2_yes(tmp_path: Path):
    img = tmp_path / "fw.uf2"
    img.write_bytes(b"uf2" * 1000)
    dest = tmp_path / "vol" / "fw.uf2"
    live: list[str] = []
    result = first_flash(image=img, uf2_dest=dest, yes=True, on_progress=live.append)
    assert result.ok
    assert dest.is_file()
    assert any("uf2-copy" in x for x in live)


def test_cli_first_flash_help():
    from silico.cli import build_parser

    p = build_parser()
    args = p.parse_args(
        ["first-flash", "x.bin", "--port", "COM1", "--yes", "--chip", "esp32"]
    )
    assert args.image == "x.bin"
    assert args.port == "COM1"
    assert args.yes is True


def test_stage_header():
    assert stage_header("write", "go") == "PROGRESS [write] go"
