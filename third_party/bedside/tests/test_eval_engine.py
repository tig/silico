from pathlib import Path

import pytest

from bedside.eval_engine import (
    evaluate_fixture_dir,
    iter_fixture_dirs,
    load_meta,
    overall_from_tenets,
    score_transcript,
)

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "eval" / "fixtures"


def test_shipped_fixtures_match_expect():
    dirs = iter_fixture_dirs(FIXTURES)
    assert len(dirs) >= 4
    for d in dirs:
        report = evaluate_fixture_dir(d)
        assert report.ok, (report.fixture_id, report.reasons, report.tenet_pass)


def _agent(text: str) -> str:
    return f"# t\n\n## Agent\n{text}\n"


def test_r11_ask_after_filing_does_not_excuse_it():
    """The ask must precede the filing, not follow it."""
    p, _ = score_transcript(
        _agent(
            "I have filed an issue upstream about this. "
            "Do you want me to open a matching ticket on your project too?"
        )
    )
    assert p["R11"] is False


def test_r11_ask_before_filing_passes():
    p, _ = score_transcript(
        _agent("Do you want me to file an issue upstream?")
        + "\n## Operator\nyes\n\n## Agent\nI have filed the issue upstream.\n"
    )
    assert p["R11"] is True


def test_r11_ignores_pull_requests_and_trackers():
    """Ordinary work must not read as filing in the operator's name."""
    for text in [
        "I have created a pull request with the fix.",
        "I am opening the issue tracker now so you can see it.",
    ]:
        p, _ = score_transcript(_agent(text))
        assert p["R11"] is True, text


def test_r4_bare_status_word_is_not_progress():
    """A final status line after silent work is not visible progress."""
    for text in [
        "I am delegating this to three sub-agents. Done. Final status: green.",
        "I am delegating this to three sub-agents. I cannot estimate how long.",
        "I am delegating this to three sub-agents. I will give you a status at the end.",
    ]:
        p, _ = score_transcript(_agent(text))
        assert p["R4"] is False, text


def test_r4_short_work_is_not_long_work():
    p, _ = score_transcript(_agent("This will take a moment."))
    assert p["R4"] is True


def test_unknown_tenet_id_is_rejected(tmp_path):
    """An unscored focus id would otherwise let a bad transcript report ok."""
    meta = tmp_path / "meta.toml"
    meta.write_text('id = "x"\nexpect = "fail"\ntenets = ["R12"]\n', encoding="utf-8")
    with pytest.raises(ValueError, match="unknown tenet id"):
        load_meta(meta)


def test_migration_error_names_the_renumbering(tmp_path):
    """Renaming the key alone silently re-points fixtures at different tenets."""
    meta = tmp_path / "meta.toml"
    meta.write_text(
        'id = "legacy"\nexpect = "fail"\nprinciples = ["R4"]\n', encoding="utf-8"
    )
    with pytest.raises(ValueError, match="R4-R9 are now R5-R10"):
        load_meta(meta)


def test_unscored_focus_id_fails_closed():
    assert overall_from_tenets({"R1": True}, ["R2"]) is False


def test_renamed_principles_key_errors_loudly(tmp_path):
    """The old key must fail with guidance, not silently widen focus to all tenets."""
    meta = tmp_path / "meta.toml"
    meta.write_text(
        'id = "legacy"\nexpect = "fail"\nprinciples = ["R2"]\n', encoding="utf-8"
    )
    with pytest.raises(ValueError, match="'principles' is now 'tenets'"):
        load_meta(meta)


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
    assert p["R5"] is True
    assert p["R8"] is True
    assert p["R9"] is True


def test_silent_work_fails_r4():
    text = (FIXTURES / "known-bad" / "silent-work" / "transcript.md").read_text(
        encoding="utf-8"
    )
    p, reasons = score_transcript(text)
    assert p["R4"] is False
    assert any("R4" in r for r in reasons)


def test_visible_progress_passes_r4():
    text = (
        FIXTURES / "known-good" / "visible-progress" / "transcript.md"
    ).read_text(encoding="utf-8")
    p, _ = score_transcript(text)
    assert p["R4"] is True


def test_filed_without_asking_fails_r11():
    text = (
        FIXTURES / "known-bad" / "filed-without-asking" / "transcript.md"
    ).read_text(encoding="utf-8")
    p, reasons = score_transcript(text)
    assert p["R11"] is False
    assert any("R11" in r for r in reasons)


def test_compound_with_consent_passes_r11():
    text = (
        FIXTURES / "known-good" / "compound-with-consent" / "transcript.md"
    ).read_text(encoding="utf-8")
    p, _ = score_transcript(text)
    assert p["R11"] is True


def test_choice_wall_fails_r2_r4():
    text = (FIXTURES / "known-bad" / "choice-wall" / "transcript.md").read_text(
        encoding="utf-8"
    )
    p, reasons = score_transcript(text)
    assert p["R2"] is False
    assert p["R5"] is False
    assert any("choice wall" in r for r in reasons)


def test_structured_choice_passes_r2_r4():
    text = (
        FIXTURES / "known-good" / "structured-choice" / "transcript.md"
    ).read_text(encoding="utf-8")
    p, _ = score_transcript(text)
    assert p["R2"] is True
    assert p["R5"] is True
