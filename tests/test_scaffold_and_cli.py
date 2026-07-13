from pathlib import Path

from silico.cli import main
from silico.scaffold import plate_root, scaffold


def test_plate_root_exists():
    root = plate_root()
    assert (root / "firmware" / "version.py").is_file()
    assert (root / "sim" / "test_host_gate.py").is_file()
    assert (root / ".gitignore").is_file()


def test_scaffold_into_empty(tmp_path: Path):
    dest = tmp_path / "gcu"
    lines = scaffold(dest)
    assert (dest / "firmware" / "version.py").is_file()
    assert (dest / "requirements-dev.txt").is_file()
    assert (dest / ".gitignore").is_file()
    assert any("written" in x for x in lines)
    # no bytecode
    assert not any(p.suffix == ".pyc" for p in dest.rglob("*"))
    assert not any(p.name == "__pycache__" for p in dest.rglob("*"))


def test_scaffold_merges_without_clobbering_product_readme(tmp_path: Path):
    dest = tmp_path / "gcu"
    dest.mkdir()
    (dest / "README.md").write_text("# Zakalwe product\n", encoding="utf-8")
    (dest / "spec.md").write_text("# domain\n", encoding="utf-8")
    lines = scaffold(dest)  # no --force needed
    assert (dest / "firmware" / "version.py").is_file()
    assert (dest / "README.md").read_text(encoding="utf-8") == "# Zakalwe product\n"
    assert (dest / "spec.md").read_text(encoding="utf-8") == "# domain\n"
    assert any("protect product" in x for x in lines)


def test_scaffold_force_still_protects_readme(tmp_path: Path):
    dest = tmp_path / "gcu"
    dest.mkdir()
    (dest / "README.md").write_text("# keep me\n", encoding="utf-8")
    scaffold(dest, force=True)
    assert (dest / "README.md").read_text(encoding="utf-8") == "# keep me\n"


def test_cli_version():
    assert main(["version"]) == 0


def test_cli_doctor():
    assert main(["doctor"]) in (0, 1)


def test_deploy_requires_port(tmp_path: Path):
    f = tmp_path / "version.py"
    f.write_text("FW_NAME='X'\nFW_VERSION='0.0.1'\n", encoding="utf-8")
    # argparse requires --port (SystemExit on missing required flag)
    try:
        main(["deploy", str(f)])
        assert False, "expected SystemExit for missing --port"
    except SystemExit as e:
        assert e.code != 0


def test_deploy_help_mentions_manifest():
    # files are optional nargs=*
    from silico.cli import build_parser

    p = build_parser()
    # ensure deploy subparser accepts zero files
    args = p.parse_args(["deploy", "--port", "COM9"])
    assert args.files == []


def test_deploy_plan_lines_mention_confirmation(tmp_path: Path, monkeypatch):
    from silico import deploy as deploy_mod
    from silico.ports import PortInfo

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
    assert "--yes" in text or "confirmation" in text.lower()
    assert "OVERWRITE" in text
    assert "CONFIRM" in text
    assert main(["deploy", str(f), "--port", "COM9"]) == 2


def test_deploy_plan_fails_if_port_not_listed(tmp_path: Path, monkeypatch):
    from silico import deploy as deploy_mod
    from silico.ports import PortInfo

    f = tmp_path / "version.py"
    f.write_text("FW_NAME='X'\nFW_VERSION='0.0.1'\n", encoding="utf-8")
    monkeypatch.setattr(deploy_mod, "mpremote_available", lambda: True)
    monkeypatch.setattr(
        deploy_mod,
        "pick_best_port",
        lambda explicit=None: PortInfo(
            device="COM9",
            vid=None,
            pid=None,
            description="",
            manufacturer="",
            score=0,
            label="missing",
        ),
    )
    monkeypatch.setattr(deploy_mod, "port_is_listed", lambda _d: False)
    plan = deploy_mod.plan_deploy([f], port="COM9")
    assert isinstance(plan, deploy_mod.DeployResult)
    assert plan.ok is False


def test_deploy_yes_without_confirm_flag_still_aborts(tmp_path: Path, monkeypatch):
    from silico import deploy as deploy_mod
    from silico.ports import PortInfo

    f = tmp_path / "main.py"
    f.write_text("x=1\n", encoding="utf-8")
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
    wrote = {"n": 0}

    def boom(*_a, **_k):
        wrote["n"] += 1
        raise AssertionError("cp_to_device must not run without yes=True")

    monkeypatch.setattr(deploy_mod, "cp_to_device", boom)
    result = deploy_mod.deploy([f], port="COM9", yes=False)
    assert result.ok is False
    assert wrote["n"] == 0
