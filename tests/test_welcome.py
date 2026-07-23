"""Stage 0 orientation: silico welcome skeleton must be complete before start gate."""

from pathlib import Path

from silico.welcome import (
    ORIENTATION_MARKERS,
    build_welcome,
    validate_orientation_text,
)


def test_orientation_markers_cover_required_skeleton():
    keys = {m[0] for m in ORIENTATION_MARKERS}
    assert "silico" in keys
    assert "gcu" in keys
    assert "role" in keys
    assert "readiness" in keys
    assert "first_ship_map" in keys
    assert "next_step" in keys
    assert "start_gate_after" in keys


def test_thin_tooling_status_fails_orientation_eval():
    thin = """
Git OK, Python 3.12 OK, gh logged in.
Workspace mode: gcu
Serial ports: COM3 demoted.
Ready to start first ship?
"""
    missing = validate_orientation_text(thin)
    assert missing
    assert any(m in ("silico", "gcu", "first_ship_map") for m in missing)


def test_full_skeleton_passes_orientation_eval():
    good = """
Welcome. **Silico** is the open host-first spine for building shippable edge products.

This session builds a **GCU** (General Contact Unit — Silico's term for one shippable edge product).

I'm here to get it shipped. I own the host path; the operator owns product judgment and physical/irreversible steps.

What I know now: Git OK, Python OK; workspace mode=gcu; no preferred board on USB yet.

**first-ship map:** (A) machine tools → (B) workspace → (C) plate + host gate → (D) board talks over USB.

**Next after go:** clone Silico locally and scaffold the plate.

Start gate is next — do not open the start-first-ship chooser until this orientation is shown.
"""
    assert validate_orientation_text(good) == []


def test_build_welcome_passes_orientation_eval(tmp_path: Path):
    (tmp_path / "README.md").write_text(
        "# Demo Product\n\nA pocket status light for the bench.\n",
        encoding="utf-8",
    )
    (tmp_path / "spec.md").write_text(
        "# Spec\n\nIntent: blink a status LED.\n",
        encoding="utf-8",
    )
    (tmp_path / "silico.toml").write_text(
        '[product]\nname = "Demo"\n',
        encoding="utf-8",
    )
    lines = build_welcome(root=tmp_path)
    text = "\n".join(lines)
    missing = validate_orientation_text(text)
    assert missing == [], f"welcome missing {missing}:\n{text}"
    assert "Silico" in text
    assert "GCU" in text
    assert "first ship" in text.lower() or "first-ship" in text.lower()
    assert "start gate" in text.lower() or "start-first-ship" in text.lower()
    assert "Demo" in text or "blink" in text.lower() or "status" in text.lower()


def test_build_welcome_thin_docs_is_honest(tmp_path: Path):
    (tmp_path / "silico.toml").write_text("[product]\nname = \"X\"\n", encoding="utf-8")
    text = "\n".join(build_welcome(root=tmp_path))
    assert validate_orientation_text(text) == []
    assert "thin" in text.lower() or "spec" in text.lower() or "README" in text


def test_welcome_is_cp1252_safe(tmp_path: Path):
    """Windows legacy consoles use cp1252; U+2192 etc. used to crash silico welcome."""
    (tmp_path / "silico.toml").write_text("[product]\nname = \"X\"\n", encoding="utf-8")
    text = "\n".join(build_welcome(root=tmp_path))
    text.encode("cp1252")  # must not raise
    assert "\u2192" not in text
    assert "AGENT:" in text
    assert "0a" in text


def test_welcome_encodes_canonical_start_gate(tmp_path: Path):
    """Agents invent Go/Host-only pickers when the tool does not print the shape."""
    (tmp_path / "silico.toml").write_text("[product]\nname = \"X\"\n", encoding="utf-8")
    text = "\n".join(build_welcome(root=tmp_path))
    assert "start-first-ship" in text
    assert "yes,adjust" in text or ("yes" in text and "adjust" in text)
    assert "Host-only" in text  # named ban
    assert "tool log only" in text.lower() or "tool log only fails" in text.lower()
    assert "END THE TURN" in text or "end the turn" in text.lower() or "END THIS TURN" in text
    assert "Turn 2" in text or "turn 2" in text.lower()


def test_cli_out_survives_cp1252_stream(capsys):
    from silico.cli import _out

    # Exercise the happy path; encoding-safe path is covered when print raises.
    _out("First-ship map: A -> B -> C")
    captured = capsys.readouterr()
    assert "First-ship map" in captured.out
