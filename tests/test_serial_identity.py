"""Serial identity probe (#78 CH9102; #81 CR boot-buffer preserve)."""

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
        self.clears = 0
        self.closed = False

    def open(self) -> None:
        pass

    def close(self) -> None:
        self.closed = True

    def reset_input_buffer(self) -> None:
        self.clears += 1

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
    assert pulses == []
    assert b"identity\r\n" in fake.writes
    assert fake.clears == 1  # stale clear only when not pulsing


def test_reset_true_clears_only_before_pulse(monkeypatch):
    """Boot-only C plate: clear before pulse, never after boot wait (#81 CR)."""
    fake = _FakeSer()
    order: list[str] = []

    def _clear(s):
        order.append("clear")
        s.clears += 1

    def _pulse(s):
        order.append("pulse")

    def _listen(_s, _t):
        order.append("listen")
        return b"fw_name=GCU fw_version=0.0.1\n"

    _install_fake_serial(monkeypatch, fake)
    monkeypatch.setattr(mod, "_clear_input", _clear)
    monkeypatch.setattr(mod, "_pulse_reset", _pulse)
    monkeypatch.setattr(mod, "_listen", _listen)
    monkeypatch.setattr(mod.time, "sleep", lambda *_: order.append("boot_wait"))

    r = probe_serial_identity("COM7", reset=True, listen_s=0.01, boot_wait_s=0.1)
    assert r.ok
    assert r.identity is not None
    assert r.identity.fw_name == "GCU"
    # Exactly one clear, and it happens before pulse/boot_wait/listen
    assert order.count("clear") == 1
    assert order.index("clear") < order.index("pulse")
    assert order.index("pulse") < order.index("boot_wait")
    assert order.index("boot_wait") < order.index("listen")
    assert not any(
        order[i] == "clear" and i > order.index("pulse") for i in range(len(order))
    )


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


def test_probe_empty_reports_ch9102_hint(monkeypatch):
    fake = _FakeSer()
    _install_fake_serial(monkeypatch, fake)
    monkeypatch.setattr(mod, "_listen", lambda _s, _t: b"")
    monkeypatch.setattr(mod.time, "sleep", lambda *_: None)

    r = probe_serial_identity("COM7", listen_s=0.01)
    assert not r.ok
    assert any("CH9102" in ln for ln in r.lines)
