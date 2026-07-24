"""Session / provenance CLI (tig/silico#84)."""

from pathlib import Path

from silico.cli import main
from silico.session import SESSION_REL, show_session, start_session


def test_start_session_writes_file(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # init minimal git so rev-parse works
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "README.md").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    r = start_session(root=tmp_path, mode="evaluation", agent="codex", workflow="main")
    assert r.ok
    path = tmp_path / SESSION_REL
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "start_commit" in text
    assert "evaluation" in text
    assert "codex" in text
    assert "git reset --hard" in text
    assert any("start_commit=" in ln for ln in r.lines)


def test_show_session_requires_start(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    r = show_session(root=tmp_path)
    assert not r.ok
    assert "session start" in "\n".join(r.lines)


def test_cli_session_start_show(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "f").write_text("1\n", encoding="utf-8")
    subprocess.run(["git", "add", "f"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "c"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    assert main(["session", "start", "--mode", "evaluation", "--agent", "test"]) == 0
    assert main(["session", "show"]) == 0
