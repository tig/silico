"""silico agents --stage packs from AGENTS.md (#79)."""

from __future__ import annotations

from pathlib import Path

from silico.agents_stage import (
    agents_md_path,
    index_stages,
    list_stage_ids,
    normalize_stage,
    stage_pack,
)


SAMPLE = """\
# AGENTS.md

### Manners tools are the operator path (required, not optional)

Hard rule body core.

### Operator gates: `bedside ask` / `bedside step` (not multi-choice free text)

Gates body.

### Stage 0 - Welcome the operator (proactive, safe)

Stage zero body with start gate.

### Stage D - Talk to real hardware (hello metal)

Metal body.

### C / ESP-IDF backend (`language = c`)

C backend body.

## Other section

Not a stage pack.
"""


def test_normalize_stage_aliases():
    assert normalize_stage("d") == "d"
    assert normalize_stage("metal") == "d"
    assert normalize_stage("lang-c") == "lang-c"
    assert normalize_stage("idf") == "lang-c"
    assert normalize_stage("core") == "core"
    assert normalize_stage("nope") is None


def test_index_and_stage_pack_from_text():
    idx = index_stages(SAMPLE)
    assert "0" in idx
    assert "d" in idx
    assert "core" in idx
    assert "lang-c" in idx
    ok, lines = stage_pack("d", text=SAMPLE)
    assert ok
    joined = "\n".join(lines)
    assert "hello metal" in joined.lower() or "Stage D" in joined
    assert "Stage 0" not in joined or "stage pack" in joined.lower()
    # body of D present, body of 0 not
    assert "Metal body" in joined
    assert "Stage zero body" not in joined


def test_stage_pack_list():
    ok, lines = stage_pack("list", text=SAMPLE)
    assert ok
    joined = "\n".join(lines)
    assert "Available" in joined
    assert "core" in joined
    assert "d" in joined


def test_real_agents_md_has_stages():
    path = agents_md_path()
    assert path is not None and path.is_file()
    text = path.read_text(encoding="utf-8")
    ids = dict(list_stage_ids(text))
    assert "0" in ids
    assert "d" in ids
    assert "core" in ids
    ok, lines = stage_pack("core", agents_path=path)
    assert ok
    assert any("manners" in ln.lower() or "required" in ln.lower() for ln in lines)
    ok_d, lines_d = stage_pack("d", agents_path=path)
    assert ok_d
    # stage d pack must not dump entire AGENTS
    full_len = len(text)
    pack_len = sum(len(ln) + 1 for ln in lines_d)
    assert pack_len < full_len * 0.5


def test_cli_agents_stage(capsys):
    from silico.cli import main

    rc = main(["agents", "--stage", "list"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Available" in out or "stage" in out.lower()
