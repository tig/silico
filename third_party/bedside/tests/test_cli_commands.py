from pathlib import Path

from bedside.cli import main
from bedside.commands.doctor_cmd import run_doctor
from bedside.commands.init_cmd import run_init
from bedside.exit_codes import MANNERS_FAIL, OK, SETUP_ERROR


def test_init_and_doctor(tmp_path: Path):
    # point contract at this repo's contract for doctor OK
    repo = Path(__file__).resolve().parents[1]
    r = run_init(
        tmp_path,
        pin="v0.1.0",
        contract_path=str((repo / "contract").resolve()),
    )
    assert r.exit_code == OK
    assert (tmp_path / "bedside.toml").is_file()
    assert (tmp_path / "AGENTS.md").is_file()
    assert (tmp_path / "BEDSIDE.md").is_file()

    d = run_doctor(tmp_path)
    assert d.exit_code == OK, d.messages


def test_init_refuses_without_force(tmp_path: Path):
    run_init(tmp_path)
    r = run_init(tmp_path)
    assert r.exit_code == SETUP_ERROR


def test_eval_cli_shipped_fixtures():
    repo = Path(__file__).resolve().parents[1]
    code = main(["--root", str(repo), "eval", str(repo / "eval" / "fixtures")])
    assert code == OK


def test_eval_cli_detects_mismatch(tmp_path: Path):
    # craft a "known-good" that is actually a shell wall
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
