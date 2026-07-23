"""Serial identity probe (#78 CH9102: default no DTR/RTS pulse)."""

from __future__ import annotations

import silico.serial_identity as mod
from silico.serial_identity import probe_serial_identity


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


def test_default_reset_is_false_never_pulses(monkeypatch):
    fake = _FakeSer()
    pulses: list[int] = []
    _install_fake_serial(monkeypatch, fake)
    monkeypatch.setattr(mod, "_pulse_reset", lambda _s: pulses.append(1))
    monkeypatch.setattr(
        mod, "_listen", lambda _s, _t: b"fw_name=XUSSC fw_version=0.0.1\n"
    )
    monkeypatch.setattr(mod.time, "sleep", lambda *_: None)

    r = probe_serial_identity("COM7", listen_s=0.01)
    assert r.ok
    assert r.identity is not None
    assert r.identity.fw_name == "XUSSC"
    assert r.identity.fw_version == "0.0.1"
    assert pulses == []
    assert b"identity\r\n" in fake.writes
    assert fake.dtr is False
    assert fake.rts is False
    assert any("no DTR/RTS pulse" in ln or "deasserted" in ln for ln in r.lines)


def test_reset_true_pulses_once(monkeypatch):
    fake = _FakeSer()
    pulses: list[int] = []
    _install_fake_serial(monkeypatch, fake)
    monkeypatch.setattr(mod, "_pulse_reset", lambda _s: pulses.append(1))
    monkeypatch.setattr(
        mod, "_listen", lambda _s, _t: b"fw_name=XUSSC fw_version=0.0.1\n"
    )
    monkeypatch.setattr(mod.time, "sleep", lambda *_: None)

    r = probe_serial_identity("COM7", reset=True, listen_s=0.01, boot_wait_s=0.0)
    assert r.ok
    assert pulses == [1]
    assert any("Pulse DTR/RTS" in ln for ln in r.lines)


def test_probe_empty_reports_ch9102_hint(monkeypatch):
    fake = _FakeSer()
    _install_fake_serial(monkeypatch, fake)
    monkeypatch.setattr(mod, "_listen", lambda _s, _t: b"")
    monkeypatch.setattr(mod.time, "sleep", lambda *_: None)

    r = probe_serial_identity("COM7", listen_s=0.01)
    assert not r.ok
    assert any("CH9102" in ln for ln in r.lines)
    assert "..." in "\n".join(r.lines)  # ASCII ellipsis, not U+2026
