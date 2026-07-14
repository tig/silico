from pathlib import Path

from silico.product_path import (
    load_shipped_defaults,
    resolve_defaults_path,
    run_product_path_check,
)
from silico.scaffold import scaffold


def test_plate_has_defaults_and_product_path(tmp_path: Path):
    dest = tmp_path / "gcu"
    scaffold(dest)
    assert resolve_defaults_path(dest) is not None
    defaults = load_shipped_defaults(dest)
    assert "TICK_SLEEP_MS" in defaults
    report = run_product_path_check(dest)
    assert report.ok, "\n".join(report.lines)
    assert report.sim_refs >= 1


def test_product_path_fails_without_sim_refs(tmp_path: Path):
    dest = tmp_path / "gcu"
    scaffold(dest)
    # Replace sim with a test that never mentions defaults / product_path.
    for p in (dest / "sim").rglob("*.py"):
        p.write_text("def test_noop():\n    assert True\n", encoding="utf-8")
    report = run_product_path_check(dest)
    assert not report.ok
    assert any("FAIL" in line for line in report.lines)


def test_cli_product_path(tmp_path: Path, monkeypatch):
    from silico.cli import main

    dest = tmp_path / "gcu"
    scaffold(dest)
    monkeypatch.chdir(dest)
    assert main(["product-path"]) == 0


def test_skip_ok_without_defaults_module(tmp_path: Path):
    dest = tmp_path / "empty"
    dest.mkdir()
    (dest / "sim").mkdir()
    report = run_product_path_check(dest)
    assert report.ok
    assert any("skipped" in line.lower() or "no firmware/defaults" in line for line in report.lines)


def _plate(tmp_path: Path, sim_src: str, *, toml: str | None = None) -> Path:
    (tmp_path / "firmware").mkdir()
    (tmp_path / "firmware" / "defaults.py").write_text(
        "TICK_SLEEP_MS = 250\nLED_PIN = 16\n", encoding="utf-8"
    )
    (tmp_path / "sim").mkdir()
    (tmp_path / "sim" / "test_thing.py").write_text(sim_src, encoding="utf-8")
    if toml is not None:
        (tmp_path / "silico.toml").write_text(toml, encoding="utf-8")
    return tmp_path


def test_mentioning_product_path_in_a_name_or_comment_does_not_pass(tmp_path: Path):
    """The gate must not be satisfiable by a comment.

    The old raw-source scan accepted the literal token `product_path` anywhere in
    the file, so a test name or docstring passed while the suite still exercised
    only injected constants — the exact failure this check exists to catch.
    """
    root = _plate(
        tmp_path,
        '"""Covers the product_path and shipped_defaults."""\n'
        "\n"
        "# product_path: shipped_defaults\n"
        "def test_product_path_shipped_defaults():\n"
        "    kp = 0.08\n"
        "    assert kp\n",
    )
    report = run_product_path_check(root)

    assert report.ok is False
    assert report.sim_refs == 0
    assert any("no sim test actually loads it" in line for line in report.lines)


def test_real_import_passes(tmp_path: Path):
    root = _plate(
        tmp_path,
        "import defaults\n\n\ndef test_uses_shipped():\n    assert defaults.TICK_SLEEP_MS\n",
    )
    report = run_product_path_check(root)
    assert report.ok is True
    assert report.sim_refs == 1


def test_dynamic_load_passes(tmp_path: Path):
    """The plate's own idiom: _load("defaults") rather than a bare import."""
    root = _plate(
        tmp_path,
        'def _load(name):\n    return name\n\n\ndef test_uses_shipped():\n'
        '    d = _load("defaults")\n    assert d\n',
    )
    report = run_product_path_check(root)
    assert report.ok is True
    assert report.sim_refs == 1


def test_declared_but_missing_defaults_fails(tmp_path: Path):
    """A dangling [host].product_defaults must fail, not silently skip."""
    (tmp_path / "sim").mkdir()
    (tmp_path / "sim" / "test_thing.py").write_text("def test_x():\n    pass\n", encoding="utf-8")
    (tmp_path / "silico.toml").write_text(
        '[host]\nproduct_defaults = "firmware/defaultz.py"\n', encoding="utf-8"
    )

    report = run_product_path_check(tmp_path)

    assert report.ok is False
    assert any("does not exist" in line for line in report.lines)


def test_unconfigured_and_absent_still_skips(tmp_path: Path):
    """No defaults module and none declared: skip, not fail. GCUs without a
    control loop should not be forced to invent a parameter table."""
    (tmp_path / "sim").mkdir()
    report = run_product_path_check(tmp_path)
    assert report.ok is True
    assert report.defaults_path is None
