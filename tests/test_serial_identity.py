"""Serial identity probe (#78 CH9102: no DTR/RTS pulse before knock)."""

from __future__ import annotations

import silico.serial_identity as mod
from silico.serial_identity import _attempt_plans, probe_serial_identity


class _FakeSer:
    def __init__(self) -> None:
        self.port = None
        self.baudrate = 0
        self.timeout = 0
        self.write_timeout = 0
        self.dtr = False
        self.rts = False
        self.writes: list[bytes] = []
        self.closed = False

    def open(self) -> None:
        pass

    def close(self) -> None:
        self.closed = True

    def reset_input_buffer(self) -> None:
        pass

    def write(self, data: bytes) -> int:
        self.writes.append(data)
        return len(data)

    def read(self, size: int = 1) -> bytes:
        return b""


def _install_fake_serial(monkeypatch, fake: _FakeSer) -> None:
    class _SerialMod:
        Serial = staticmethod(lambda: fake)

    monkeypatch.setitem(__import__("sys").modules, "serial", _SerialMod)


def test_attempt_plans_auto_prefers_no_pulse_first():
    plans = _attempt_plans(None)
    assert plans[0] == ("lines held deasserted (no pulse)", False)
    assert plans[1][1] is True


def test_attempt_plans_false_never_pulses():
    assert _attempt_plans(False) == [("lines held deasserted (no pulse)", False)]


def test_attempt_plans_true_pulse_only():
    assert _attempt_plans(True) == [("DTR/RTS pulse", True)]


def test_probe_reset_false_never_pulses(monkeypatch):
    fake = _FakeSer()
    pulses: list[int] = []
    _install_fake_serial(monkeypatch, fake)
    monkeypatch.setattr(mod, "_pulse_reset", lambda _s: pulses.append(1))
    monkeypatch.setattr(
        mod, "_listen", lambda _s, _t: b"fw_name=XUSSC fw_version=0.0.1\n"
    )
    monkeypatch.setattr(mod.time, "sleep", lambda *_: None)

    r = probe_serial_identity("COM7", reset=False, listen_s=0.01)
    assert r.ok
    assert r.identity is not None
    assert r.identity.fw_name == "XUSSC"
    assert r.identity.fw_version == "0.0.1"
    assert pulses == []
    assert b"identity\r\n" in fake.writes
    assert fake.dtr is False
    assert fake.rts is False


def test_probe_auto_no_pulse_succeeds_without_fallback(monkeypatch):
    fake = _FakeSer()
    pulses: list[int] = []
    _install_fake_serial(monkeypatch, fake)
    monkeypatch.setattr(mod, "_pulse_reset", lambda _s: pulses.append(1))
    monkeypatch.setattr(
        mod, "_listen", lambda _s, _t: b"fw_name=XUSSC fw_version=0.0.1\n"
    )
    monkeypatch.setattr(mod.time, "sleep", lambda *_: None)

    r = probe_serial_identity("COM7", reset=None, listen_s=0.01)
    assert r.ok
    assert pulses == []  # first attempt worked
    assert any("deasserted" in ln for ln in r.lines)


def test_probe_auto_falls_back_to_pulse(monkeypatch):
    fake = _FakeSer()
    pulses: list[int] = []
    listens = {"n": 0}

    def _listen(_s, _t):
        listens["n"] += 1
        if listens["n"] == 1:
            return b""
        return b"fw_name=XUSSC fw_version=0.0.1\n"

    _install_fake_serial(monkeypatch, fake)
    monkeypatch.setattr(mod, "_pulse_reset", lambda _s: pulses.append(1))
    monkeypatch.setattr(mod, "_listen", _listen)
    monkeypatch.setattr(mod.time, "sleep", lambda *_: None)

    r = probe_serial_identity("COM7", reset=None, listen_s=0.01, boot_wait_s=0.0)
    assert r.ok
    assert pulses == [1]
    assert any("Pulse DTR/RTS" in ln for ln in r.lines)
    assert fake.writes.count(b"identity\r\n") >= 2


def test_probe_empty_reports_ch9102_hint(monkeypatch):
    fake = _FakeSer()
    _install_fake_serial(monkeypatch, fake)
    monkeypatch.setattr(mod, "_listen", lambda _s, _t: b"")
    monkeypatch.setattr(mod.time, "sleep", lambda *_: None)

    r = probe_serial_identity("COM7", reset=False, listen_s=0.01)
    assert not r.ok
    assert any("CH9102" in ln for ln in r.lines)
