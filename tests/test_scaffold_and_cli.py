from pathlib import Path

from silico.cli import main
from silico.scaffold import plate_root, scaffold


def test_plate_root_exists():
    root = plate_root()
    assert (root / "firmware" / "version.py").is_file()
    assert (root / "sim" / "test_host_gate.py").is_file()
    assert (root / ".gitignore").is_file()


def test_plate_root_gcu_c_exists():
    root = plate_root("gcu-c")
    assert (root / "silico.toml").is_file()
    assert (root / "include" / "gcu" / "defaults.h").is_file()
    assert (root / "host" / "CMakeLists.txt").is_file()
    assert (root / "firmware" / "main" / "main.c").is_file()


def test_scaffold_gcu_c(tmp_path: Path):
    dest = tmp_path / "hello-c"
    lines = scaffold(dest, plate="gcu-c")
    assert (dest / "silico.toml").is_file()
    assert "language = \"c\"" in (dest / "silico.toml").read_text(encoding="utf-8")
    assert (dest / "src" / "domain.c").is_file()
    assert any("gcu-c" in x or "Plate: gcu-c" in x for x in lines)


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


def test_plate_host_pin_is_sibling_local_clone():
    """first ship + CI both use sibling ../silico — not a git+https pip URL."""
    root = plate_root()
    req_lines = [
        ln.strip()
        for ln in (root / "requirements-dev.txt").read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    assert any(ln == "-e ../silico" or ln.startswith("-e ../silico") for ln in req_lines)
    assert not any("git+https://github.com/tig/silico" in ln for ln in req_lines)


def test_plate_ci_sibling_silico_layout():
    """CI must place silico as a sibling so `pip install -r` can use -e ../silico.

    Anti-pattern (broke first ship GCUs): checkout only the GCU, then
    ``pip install -r requirements-dev.txt`` → missing ../silico on the runner.
    """
    root = plate_root()
    ci = root / ".github" / "workflows" / "ci.yml"
    assert ci.is_file(), "plate must ship host-gate CI"
    text = ci.read_text(encoding="utf-8")
    assert "path: gcu" in text
    assert "path: silico" in text
    assert "repository: tig/silico" in text
    assert "working-directory: gcu" in text
    assert "pip install -r requirements-dev.txt" in text
    # Do not invent a silico-src path that diverges from the first ship pin.
    assert "silico-src" not in text


def test_scaffold_ships_ci_workflow(tmp_path: Path):
    dest = tmp_path / "gcu"
    scaffold(dest)
    assert (dest / ".github" / "workflows" / "ci.yml").is_file()
    assert "path: silico" in (dest / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )


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


def test_apply_mpy_pin_requires_explicit_port(tmp_path):
    """The mutating path may not act on a guessed board.

    Port scoring is a hint, not an identification; on a bench with two RP2040s it
    can pin the product repo to the wrong board's ABI.
    """
    from silico.inspect_device import inspect

    report = inspect(port=None, apply_mpy_pin=True, root=tmp_path)

    assert report.ok is False
    assert any("requires an explicit --port" in line for line in report.lines)
    # And it wrote nothing.
    assert not (tmp_path / "silico.toml").exists()
    assert not (tmp_path / "requirements-dev.txt").exists()


def test_scaffold_writes_when_plate_lives_under_a_venv_path(tmp_path, monkeypatch):
    """Regression for #48: skip names must be tested against the path relative
    to the plate root, not the absolute source path. A venv inside the
    destination repo (the first ship layout) puts ".venv" in every absolute plate
    path and silently skipped the entire plate."""
    from silico import scaffold as sc

    fake_plate = tmp_path / ".venv" / "Lib" / "site-packages" / "silico" / "plates" / "gcu"
    (fake_plate / "firmware").mkdir(parents=True)
    (fake_plate / "firmware" / "main.py").write_text("# plate\n", encoding="utf-8")
    (fake_plate / "silico.toml").write_text("[deploy]\ncore = []\n", encoding="utf-8")

    monkeypatch.setattr(sc, "plate_root", lambda _plate="gcu": fake_plate)
    dest = tmp_path / "gcu"
    lines = sc.scaffold(dest)

    assert (dest / "firmware" / "main.py").exists()
    assert not any(l.startswith("WARN:") for l in lines)


def test_scaffold_zero_writes_on_fresh_dest_warns(tmp_path, monkeypatch):
    """A fresh scaffold that writes nothing is never what the operator meant."""
    from silico import scaffold as sc

    fake_plate = tmp_path / "plate"
    (fake_plate / "__pycache__").mkdir(parents=True)
    (fake_plate / "__pycache__" / "junk.py").write_text("x", encoding="utf-8")

    monkeypatch.setattr(sc, "plate_root", lambda _plate="gcu": fake_plate)
    lines = sc.scaffold(tmp_path / "fresh")

    assert any(l.startswith("WARN:") for l in lines)


def test_run_mpremote_knocks_protocol_door_on_raw_repl_failure(monkeypatch):
    """Regression for #49: on 'could not enter raw repl', knock with `repl`
    and retry once; if still failing, explain the hardened console."""
    import subprocess as sp
    from silico import mpremote_util as mu

    calls = {"run": 0, "knock": 0}

    def fake_run(cmd, **kw):
        calls["run"] += 1
        if calls["run"] == 1:
            return sp.CompletedProcess(cmd, 1, stdout="", stderr="could not enter raw repl\n")
        return sp.CompletedProcess(cmd, 0, stdout="ok\n", stderr="")

    def fake_knock(port, wait_s=2.5):
        calls["knock"] += 1
        return True

    monkeypatch.setattr(mu.subprocess, "run", fake_run)
    monkeypatch.setattr(mu, "knock_protocol_door", fake_knock)

    r = mu.run_mpremote("COM6", "ls", ":")
    assert r.returncode == 0
    assert calls == {"run": 2, "knock": 1}


def test_run_mpremote_explains_when_door_stays_shut(monkeypatch):
    import subprocess as sp
    from silico import mpremote_util as mu

    def fake_run(cmd, **kw):
        return sp.CompletedProcess(cmd, 1, stdout="", stderr="could not enter raw repl\n")

    monkeypatch.setattr(mu.subprocess, "run", fake_run)
    monkeypatch.setattr(mu, "knock_protocol_door", lambda port, wait_s=2.5: True)

    r = mu.run_mpremote("COM6", "ls", ":")
    assert r.returncode == 1
    assert "owns the console" in r.stderr
    assert "#49" in r.stderr and "#62" in r.stderr
    # Lockout recovery must be first-class: thrash ban + one-shot reflash recipe.
    assert "Do NOT thrash" in r.stderr
    assert "erase-flash" in r.stderr
    assert "esp32-usb-serial.md" in r.stderr


def test_gate_fails_on_future_import_in_deploy_set(tmp_path):
    """Regression for #46: a deploy-set file importing __future__ verifies on
    the host and dies on device before the loop starts. The gate must catch
    the class, not just the plate instance."""
    (tmp_path / "firmware").mkdir()
    (tmp_path / "firmware" / "version.py").write_text(
        'FW_NAME = "X"\nFW_VERSION = "0.0.1"\n', encoding="utf-8"
    )
    (tmp_path / "firmware" / "bad.py").write_text(
        "from __future__ import annotations\nX = 1\n", encoding="utf-8"
    )
    (tmp_path / "silico.toml").write_text(
        '[deploy]\ncore = ["firmware/version.py", "firmware/bad.py"]\n',
        encoding="utf-8",
    )

    from silico.host_hygiene import run_hygiene

    report = run_hygiene(tmp_path)
    assert report.ok is False
    assert any("__future__" in l and "bad.py" in l for l in report.lines)
