from pathlib import Path

from bedside.cli import main
from bedside.commands.doctor_cmd import run_doctor
from bedside.commands.eval_cmd import run_eval
from bedside.commands.init_cmd import run_init
from bedside.eval_engine import evaluate_fixture_dir
from bedside.exit_codes import MANNERS_FAIL, OK, SETUP_ERROR


def test_init_and_doctor(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]
    r = run_init(
        tmp_path,
        pin="v0.1.0",
        contract_path=str((repo / "contract").resolve()),
        domain_fixtures="eval/fixtures",
    )
    assert r.exit_code == OK
    assert (tmp_path / "bedside.toml").is_file()
    assert (tmp_path / "AGENTS.md").is_file()
    assert (tmp_path / "BEDSIDE.md").is_file()
    toml = (tmp_path / "bedside.toml").read_text(encoding="utf-8")
    assert "fixture_paths" in toml

    d = run_doctor(tmp_path)
    assert d.exit_code == OK, d.messages


def test_init_refuses_without_force(tmp_path: Path):
    run_init(tmp_path)
    r = run_init(tmp_path)
    assert r.exit_code == SETUP_ERROR


def test_init_vendor_from(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]
    r = run_init(
        tmp_path,
        vendor_from=repo,
        force=True,
        include_src=False,
    )
    assert r.exit_code == OK, r.messages
    assert (tmp_path / "third_party" / "bedside" / "contract" / "README.md").is_file()
    assert (tmp_path / "third_party" / "bedside" / "VENDOR.md").is_file()
    assert not (tmp_path / "third_party" / "bedside" / "src").exists()
    assert (tmp_path / "eval" / "fixtures" / "known-bad").is_dir()
    d = run_doctor(tmp_path)
    assert d.exit_code == OK, d.messages


def test_eval_cli_shipped_fixtures():
    repo = Path(__file__).resolve().parents[1]
    code = main(["--root", str(repo), "eval", str(repo / "eval" / "fixtures")])
    assert code == OK


def test_eval_multi_root(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]
    # product domain root with one extra known-bad
    domain = tmp_path / "eval" / "fixtures" / "known-bad" / "extra-wall"
    domain.mkdir(parents=True)
    (domain / "meta.toml").write_text(
        'id = "extra-wall"\nexpect = "fail"\nprinciples = ["R2"]\n',
        encoding="utf-8",
    )
    (domain / "transcript.md").write_text(
        "## Agent\nRun these:\n\n```bash\npip install x\npytest\n```\n",
        encoding="utf-8",
    )
    r = run_eval(
        tmp_path,
        [repo / "eval" / "fixtures" / "known-good", tmp_path / "eval" / "fixtures"],
    )
    assert r.exit_code == OK, r.messages
    joined = "\n".join(r.messages)
    assert "extra-wall" in joined
    assert "step-and-confirm" in joined or "day2-leavebehind" in joined


def test_eval_cli_detects_mismatch(tmp_path: Path):
    fix = tmp_path / "bad-as-good"
    fix.mkdir()
    (fix / "meta.toml").write_text(
        'id = "x"\nexpect = "pass"\nprinciples = ["R2"]\n',
        encoding="utf-8",
    )
    (fix / "transcript.md").write_text(
        "## Agent\nRun these:\n\n```bash\ngit clone x\npip install y\npytest\n```\n",
        encoding="utf-8",
    )
    code = main(["--root", str(tmp_path), "eval", str(fix)])
    assert code == MANNERS_FAIL


def test_step_and_confirm_summary_uses_info_not_failed():
    repo = Path(__file__).resolve().parents[1]
    rep = evaluate_fixture_dir(repo / "eval" / "fixtures" / "known-good" / "step-and-confirm")
    assert rep.ok
    assert rep.failed_focus == []
    # R9 may fail as non-focus; must not appear in failed_focus
    r = run_eval(
        repo,
        [repo / "eval" / "fixtures" / "known-good" / "step-and-confirm"],
    )
    line = next(m for m in r.messages if "step-and-confirm" in m)
    assert "failed=" not in line
    if rep.info_failed:
        assert "info=" in line
