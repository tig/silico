"""Tests for bedside ask and step operator gates."""

from pathlib import Path

from bedside.cli import main
from bedside.commands.ask_cmd import order_choices, parse_choices, run_ask
from bedside.commands.step_cmd import run_step
from bedside.exit_codes import HUMAN_NEEDED, OK, SETUP_ERROR


def test_parse_and_order_choices():
    assert parse_choices("yes, no, maybe") == ["yes", "no", "maybe"]
    assert order_choices(["a", "b", "c"], "b") == ["b", "a", "c"]


def test_ask_recommended_exit_zero():
    r = run_ask(
        gate_id="confirm-deploy",
        prompt="Deploy to production now?",
        choices=["yes", "no"],
        default="no",
        answer="no",
    )
    assert r.exit_code == OK
    joined = "\n".join(r.messages)
    assert "Selected: no" in joined
    assert "matched_recommended: true" in joined
    assert "bedside.ask id=confirm-deploy" in joined


def test_ask_non_recommended_exit_human_needed():
    r = run_ask(
        gate_id="confirm-deploy",
        prompt="Deploy to production now?",
        choices=["yes", "no"],
        default="no",
        answer="yes",
    )
    assert r.exit_code == HUMAN_NEEDED
    assert "matched_recommended: false" in "\n".join(r.messages)


def test_ask_index_and_case():
    r = run_ask(
        gate_id="fork",
        prompt="Which path?",
        choices=["continue", "pause", "rewrite"],
        default="continue",
        answer="2",
    )
    assert r.exit_code == HUMAN_NEEDED
    assert "Selected: pause" in "\n".join(r.messages)

    r2 = run_ask(
        gate_id="fork",
        prompt="Which path?",
        choices=["continue", "pause"],
        default="continue",
        answer="CONTINUE",
    )
    assert r2.exit_code == OK


def test_ask_requires_id_prompt():
    assert run_ask(gate_id="", prompt="x").exit_code == SETUP_ERROR
    assert run_ask(gate_id="x", prompt="").exit_code == SETUP_ERROR


def test_ask_cli_missing_id_is_setup_error():
    """Argparse required flags must surface as exit 30, not argparse's 2."""
    code = main(["ask", "--prompt", "Go?"])
    assert code == SETUP_ERROR


def test_ask_case_insensitive_duplicate_choices():
    r = run_ask(
        gate_id="g",
        prompt="Go?",
        choices=["Yes", "yes"],
        answer="yes",
    )
    assert r.exit_code == SETUP_ERROR
    assert "case-insensitive" in "\n".join(r.messages)


def test_ask_noninteractive_without_answer():
    r = run_ask(
        gate_id="g",
        prompt="Go?",
        answer=None,
        stdin_isatty=False,
    )
    assert r.exit_code == HUMAN_NEEDED
    assert "Human action needed" in "\n".join(r.messages)


def test_ask_interactive_input_fn():
    r = run_ask(
        gate_id="g",
        prompt="Go?",
        choices=["yes", "no"],
        default="no",
        input_fn=lambda _p: "no",
        stdin_isatty=True,
    )
    assert r.exit_code == OK


def test_ask_json():
    r = run_ask(
        gate_id="g",
        prompt="Go?",
        default="no",
        choices=["yes", "no"],
        answer="no",
        json_out=True,
    )
    assert r.exit_code == OK
    assert r.messages[0].startswith("{")
    assert '"choice": "no"' in r.messages[0]


def test_step_confirm():
    r = run_step(
        gate_id="plug-usb",
        prompt="Plug the data USB cable into the board.",
        expect="The board shows a power LED on.",
        confirm=True,
    )
    assert r.exit_code == OK
    joined = "\n".join(r.messages)
    assert "Step: plug-usb" in joined
    assert "power LED" in joined
    assert "Confirmed: true" in joined
    assert "bedside.step id=plug-usb confirmed=true" in joined


def test_step_decline():
    r = run_step(
        gate_id="plug-usb",
        prompt="Plug the cable.",
        confirm=False,
    )
    assert r.exit_code == HUMAN_NEEDED
    assert "Confirmed: false" in "\n".join(r.messages)


def test_step_pending_noninteractive():
    r = run_step(
        gate_id="login",
        prompt="Sign in in the browser.",
        confirm=None,
        stdin_isatty=False,
    )
    assert r.exit_code == HUMAN_NEEDED
    assert "Human action needed" in "\n".join(r.messages)


def test_step_interactive_input_fn():
    r = run_step(
        gate_id="login",
        prompt="Sign in.",
        input_fn=lambda _p: "yes",
        stdin_isatty=True,
    )
    assert r.exit_code == OK


def test_step_no_wait():
    r = run_step(
        gate_id="login",
        prompt="Sign in.",
        wait_confirm=False,
    )
    assert r.exit_code == HUMAN_NEEDED
    joined = "\n".join(r.messages)
    assert "wait=false" in joined
    assert "wait=true" not in joined


def test_ask_interactive_prints_before_read(capsys):
    r = run_ask(
        gate_id="g",
        prompt="Deploy now?",
        choices=["yes", "no"],
        default="no",
        input_fn=lambda _p: "no",
        stdin_isatty=True,
    )
    assert r.exit_code == OK
    out = capsys.readouterr().out
    assert "Gate: g" in out
    assert "Deploy now?" in out
    assert "Choices (recommended first):" in out


def test_step_interactive_prints_before_read(capsys):
    r = run_step(
        gate_id="plug-usb",
        prompt="Plug the cable.",
        expect="LED on",
        input_fn=lambda _p: "yes",
        stdin_isatty=True,
    )
    assert r.exit_code == OK
    out = capsys.readouterr().out
    assert "Step: plug-usb" in out
    assert "Plug the cable." in out
    assert "LED on" in out


def test_ask_cli():
    code = main(
        [
            "ask",
            "--id",
            "confirm-deploy",
            "--prompt",
            "Deploy?",
            "--choices",
            "yes,no",
            "--default",
            "no",
            "--answer",
            "no",
        ]
    )
    assert code == OK


def test_step_cli_confirm_decline_mutex():
    code = main(
        [
            "step",
            "--id",
            "x",
            "--prompt",
            "Do it",
            "--confirm",
            "--decline",
        ]
    )
    assert code == SETUP_ERROR


def test_step_cli_confirm():
    code = main(
        [
            "step",
            "--id",
            "plug-usb",
            "--prompt",
            "Plug USB",
            "--expect",
            "LED on",
            "--confirm",
        ]
    )
    assert code == OK


def test_operator_gate_fixtures_match():
    """Shipped ask/step fixtures must exist and match expect."""
    repo = Path(__file__).resolve().parents[1]
    from bedside.commands.eval_cmd import run_eval

    for name in ("operator-gate-ask", "operator-gate-step"):
        path = repo / "eval" / "fixtures" / "known-good" / name
        assert path.is_dir(), f"missing shipped fixture: {path}"
        r = run_eval(repo, [path])
        assert r.exit_code == OK, (name, r.messages)
