from pathlib import Path

from bedside.eval_engine import evaluate_fixture_dir, iter_fixture_dirs, score_transcript

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "eval" / "fixtures"


def test_shipped_fixtures_match_expect():
    dirs = iter_fixture_dirs(FIXTURES)
    assert len(dirs) >= 4
    for d in dirs:
        report = evaluate_fixture_dir(d)
        assert report.ok, (report.fixture_id, report.reasons, report.principle_pass)


def test_shell_wall_fails_r2_r3():
    text = (FIXTURES / "known-bad" / "shell-wall" / "transcript.md").read_text(
        encoding="utf-8"
    )
    p, reasons = score_transcript(text)
    assert p["R2"] is False
    assert p["R3"] is False


def test_step_and_confirm_passes_focus():
    text = (
        FIXTURES / "known-good" / "step-and-confirm" / "transcript.md"
    ).read_text(encoding="utf-8")
    p, _ = score_transcript(text)
    assert p["R4"] is True
    assert p["R7"] is True
    assert p["R8"] is True


def test_choice_wall_fails_r2_r4():
    text = (FIXTURES / "known-bad" / "choice-wall" / "transcript.md").read_text(
        encoding="utf-8"
    )
    p, reasons = score_transcript(text)
    assert p["R2"] is False
    assert p["R4"] is False
    assert any("choice wall" in r for r in reasons)


def test_structured_choice_passes_r2_r4():
    text = (
        FIXTURES / "known-good" / "structured-choice" / "transcript.md"
    ).read_text(encoding="utf-8")
    p, _ = score_transcript(text)
    assert p["R2"] is True
    assert p["R4"] is True
