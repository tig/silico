"""Host Python / tool health pre-flight checks (#87 Mac first-ship friction)."""

from __future__ import annotations

from pathlib import Path

from silico.doctor import cmake_hint_lines, host_python_health_lines, run_doctor


def test_pyexpat_ok_on_healthy_python():
    ok, lines = host_python_health_lines()
    # The test interpreter itself must be healthy — and report OK.
    assert ok
    assert any("pyexpat" in ln and ln.startswith("OK") for ln in lines)


def test_pyexpat_broken_reports_uv_hint():
    def broken(_name):
        raise ImportError("symbol not found: _XML_SetAllocTrackerActivationThreshold")

    ok, lines = host_python_health_lines(import_module=broken)
    assert not ok
    joined = "\n".join(lines)
    assert "WARN" in joined
    assert "pyexpat" in joined
    # Actionable: broken Homebrew python linkage → use a uv-managed interpreter.
    assert "uv venv" in joined


def test_cmake_hint_when_off_path(tmp_path: Path):
    bindir = tmp_path / "opt-homebrew-bin"
    bindir.mkdir()
    (bindir / "cmake").write_text("", encoding="utf-8")
    lines = cmake_hint_lines(which=lambda _n: None, probe_dirs=[bindir])
    joined = "\n".join(lines)
    assert "WARN" in joined
    assert str(bindir / "cmake") in joined
    assert "PATH" in joined


def test_cmake_no_hint_when_on_path(tmp_path: Path):
    lines = cmake_hint_lines(which=lambda _n: "/usr/bin/cmake", probe_dirs=[tmp_path])
    assert lines == ["OK: cmake on PATH (C host gate)"]


def test_cmake_missing_everywhere(tmp_path: Path):
    lines = cmake_hint_lines(which=lambda _n: None, probe_dirs=[tmp_path])
    joined = "\n".join(lines)
    assert "WARN" in joined and "cmake" in joined


def test_run_doctor_includes_python_health():
    report = run_doctor()
    joined = "\n".join(report.lines)
    assert "pyexpat" in joined
