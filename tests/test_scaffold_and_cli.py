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


def test_gcu_c_host_gate_target_is_not_reserved_test_name():
    """#72: CMake reserves target name ``test`` when CTest is enabled.

    Plate must use ``host_test`` and ``[host].gate`` must match. A bare
    ``add_custom_target(test …)`` fails ``cmake -S host -B build/host`` on
    Windows (and anywhere enable_testing() is on).
    """
    root = plate_root("gcu-c")
    cmake = (root / "host" / "CMakeLists.txt").read_text(encoding="utf-8")
    toml = (root / "silico.toml").read_text(encoding="utf-8")
    assert "add_custom_target(host_test" in cmake
    assert "add_custom_target(test\n" not in cmake
    assert "add_custom_target(test " not in cmake
    assert "--target host_test" in toml
    assert "--target test\"" not in toml
    assert "--target test'" not in toml


def _cmake_output_missing_c_compiler(out: str) -> bool:
    """True when cmake failed because no usable C toolchain is configured.

    ``project(... C)`` needs a compiler, not only the cmake executable. Keep
    the package suite green on Python-only hosts (cmake on PATH, no VS/gcc).
    """
    lower = out.lower()
    needles = (
        "no cmake_c_compiler could be found",
        "cmake_c_compiler not set",
        "cmake_c_compiler:",
        "is not a full path and was not found in the path",
        "could not find any instance of visual studio",
        "could not find any instance of visual c",
        "does not appear to be able to compile a simple test program",
        "the c compiler",
        "unable to determine what c compiler",
        "broken compiler",
        "compiler identification is unknown",
        "failed to run msvc",
        "failed to run the project to compile",
        "nmake is not a full path",
        "no cmake_cxx_compiler could be found",
    )
    return any(n in lower for n in needles)


def _cmake_output_reserved_test_target(out: str) -> bool:
    return (
        'target name "test" is reserved' in out
        or "target name 'test' is reserved" in out
    )


def test_scaffold_gcu_c_cmake_configure_accepts_host_test(tmp_path: Path):
    """Regression for #72: configure the plate host tree (cmake -S/-B).

    Skip when cmake is missing **or** cmake is present without a usable C
    compiler (common on Python-only CI / dev machines). Always fail if
    configure dies on the reserved target name ``test``.
    """
    import shutil
    import subprocess

    import pytest

    if shutil.which("cmake") is None:
        pytest.skip("cmake not on PATH")

    dest = tmp_path / "gcu-c-cmake"
    scaffold(dest, plate="gcu-c")
    build = dest / "build" / "host"
    proc = subprocess.run(
        ["cmake", "-S", str(dest / "host"), "-B", str(build)],
        capture_output=True,
        text=True,
        check=False,
    )
    out = (proc.stdout or "") + (proc.stderr or "")

    # The bug under test — never skip this failure mode.
    assert not _cmake_output_reserved_test_target(out), out

    if proc.returncode != 0:
        if _cmake_output_missing_c_compiler(out):
            pytest.skip("cmake present but no usable C compiler/toolchain")
        # Other configure failures are environment issues, not package logic.
        # Do not fail the Python-only suite; still surface a short reason.
        snippet = out.strip().replace("\r\n", "\n")[-800:]
        pytest.skip(f"cmake configure failed (non-#72): {snippet}")


def test_plates_ship_bedside_pin_and_stage0_front_matter():
    """GCU roots must get a bedside pin + Stage 0 tool sequence agents see first.

    Harness failures: missing bedside.toml -> invent parallel path;
    plate AGENTS only soft-pointed at silico essay -> tooling dump before welcome.
    """
    for plate in ("gcu", "gcu-c"):
        root = plate_root(plate)
        assert (root / "bedside.toml").is_file(), plate
        toml = (root / "bedside.toml").read_text(encoding="utf-8")
        assert "contract_path" in toml
        assert "third_party/bedside/contract" in toml.replace("\\", "/")
        assert (root / "BEDSIDE.md").is_file(), plate
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        head = agents[:1500]
        assert "silico welcome" in head, plate
        assert "start-first-ship" in head or "start gate" in head.lower(), plate
        assert "FIRST ACTION" in head or "first action" in head.lower(), plate
        # ban pre-go init (may appear in "do not" before the welcome command line)
        assert "bedside init" in head.lower(), plate
        assert "Do not" in head or "do not" in head, plate


def test_root_agents_stage0_is_first_screen():
    """Thin GCUs only fetch silico AGENTS — Stage 0 must be above context tables.

    Observed fail: agent skims load-path tables, runs bedside init/vendor, opens
    start gate with essay, never pastes silico welcome.
    """
    root = Path(__file__).resolve().parents[1]
    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    head = agents[:4500]
    assert head.lstrip().startswith("# AGENTS.md")
    assert "FIRST ACTION" in head
    assert "silico welcome" in head
    # welcome before the long context-load section
    assert agents.find("silico welcome") < agents.find("Agent context load path")
    assert "bedside init" in head.lower()
    assert "yes,adjust" in head or "yes, adjust" in head
    assert "Host-only" in head or "host-only" in head.lower()
    assert "raw.githubusercontent.com/tig/silico/main/AGENTS.md" in head
    assert "README" in head and ("not only" in head.lower() or "not the" in head.lower())
    assert "Two turns" in head or "TURN 1" in head
    assert "same turn" in head.lower() or "same-turn" in head.lower()


def test_readme_points_agents_at_agents_md_not_homepage_only():
    """README must send agents to silico AGENTS (raw), not invent Stage 0 from digest."""
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")
    assert "raw.githubusercontent.com/tig/silico/main/AGENTS.md" in readme
    assert "not the playbook" in readme.lower()


def test_scaffold_ships_bedside_pin(tmp_path: Path):
    dest = tmp_path / "gcu"
    scaffold(dest)
    assert (dest / "bedside.toml").is_file()
    assert (dest / "BEDSIDE.md").is_file()
    dest_c = tmp_path / "gcu-c"
    scaffold(dest_c, plate="gcu-c")
    assert (dest_c / "bedside.toml").is_file()


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
