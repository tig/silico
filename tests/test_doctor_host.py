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

def _report(idf_py=None, activation=""):
    from silico.c_toolchain import CToolchainReport, IdfInstall

    selected = None
    if activation:
        selected = IdfInstall(
            name="esp-idf-5.3",
            path="/home/u/esp/esp-idf",
            idf_tools_path="/home/u/.espressif",
            activation_script=activation,
            python="",
        )
    return CToolchainReport(ok=True, idf_py=idf_py, selected=selected)


def test_esp_idf_summary_deploy_ready_is_ok():
    from silico.doctor import esp_idf_summary_lines

    lines = esp_idf_summary_lines(_report(idf_py="/usr/bin/idf.py"), deploy_ready=True)
    assert lines[0].startswith("OK")


def test_esp_idf_summary_catalog_only_is_not_ok():
    # PR #88 review (P1): catalog-only IDF must not report deploy-ready —
    # `silico deploy` only accepts idf.py on PATH or IDF_PATH.
    from silico.doctor import esp_idf_summary_lines

    lines = esp_idf_summary_lines(
        _report(idf_py="/home/u/esp/esp-idf/tools/idf.py",
                activation="/home/u/esp/esp-idf/export.sh"),
        deploy_ready=False,
    )
    joined = "\n".join(lines)
    assert not any(ln.startswith("OK") for ln in lines)
    assert "WARN" in joined
    assert "not activated" in joined or "needs activation" in joined
    assert "export.sh" in joined  # actionable activation hint


def test_esp_idf_summary_missing_is_warn():
    from silico.doctor import esp_idf_summary_lines

    lines = esp_idf_summary_lines(_report(), deploy_ready=False)
    joined = "\n".join(lines)
    assert "WARN" in joined and "not found" in joined
