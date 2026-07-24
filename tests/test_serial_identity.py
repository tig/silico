"""Serial identity probe (#78 CH9102, #79 knock retry, #81 boot-buffer preserve)."""

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


def test_attempt_plans_false_never_pulses():
    assert _attempt_plans(False) == [("lines held deasserted (no pulse)", False)]


def test_attempt_plans_true_pulse_only():
    assert _attempt_plans(True) == [("DTR/RTS pulse", True)]


def test_attempt_plans_auto_prefers_no_pulse_first():
    plans = _attempt_plans(None)
    assert plans[0] == ("lines held deasserted (no pulse)", False)
    assert plans[1][1] is True


def test_default_reset_is_false_never_pulses(monkeypatch):
    fake = _FakeSer()
    pulses: list[int] = []
    _install_fake_serial(monkeypatch, fake)
    monkeypatch.setattr(mod, "_pulse_reset", lambda _s: pulses.append(1))
    monkeypatch.setattr(
        mod,
        "_listen_with_knock_retries",
        lambda _s, _t, **_k: (b"fw_name=XUSSC fw_version=0.0.1\n", 1),
    )
    monkeypatch.setattr(mod.time, "sleep", lambda *_: None)

    r = probe_serial_identity("COM7", listen_s=0.01)
    assert r.ok
    assert r.identity is not None
    assert r.identity.fw_name == "XUSSC"
    assert pulses == []
    assert fake.dtr is False
    assert fake.rts is False
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

    def _listen(_s, _t, **_k):
        order.append("listen")
        return b"fw_name=GCU fw_version=0.0.1\n", 1

    _install_fake_serial(monkeypatch, fake)
    monkeypatch.setattr(mod, "_clear_input", _clear)
    monkeypatch.setattr(mod, "_pulse_reset", _pulse)
    monkeypatch.setattr(mod, "_listen_with_knock_retries", _listen)
    monkeypatch.setattr(mod.time, "sleep", lambda *_: order.append("boot_wait"))

    r = probe_serial_identity("COM7", reset=True, listen_s=0.01, boot_wait_s=0.1)
    assert r.ok
    assert r.identity is not None
    assert r.identity.fw_name == "GCU"
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
        mod,
        "_listen_with_knock_retries",
        lambda _s, _t, **_k: (b"fw_name=XUSSC fw_version=0.0.1\n", 1),
    )
    monkeypatch.setattr(mod.time, "sleep", lambda *_: None)

    r = probe_serial_identity("COM7", reset=True, listen_s=0.01, boot_wait_s=0.0)
    assert r.ok
    assert pulses == [1]


def test_probe_auto_no_pulse_succeeds_without_fallback(monkeypatch):
    fake = _FakeSer()
    pulses: list[int] = []
    _install_fake_serial(monkeypatch, fake)
    monkeypatch.setattr(mod, "_pulse_reset", lambda _s: pulses.append(1))
    monkeypatch.setattr(
        mod,
        "_listen_with_knock_retries",
        lambda _s, _t, **_k: (b"fw_name=XUSSC fw_version=0.0.1\n", 2),
    )
    monkeypatch.setattr(mod.time, "sleep", lambda *_: None)

    r = probe_serial_identity("COM7", reset=None, listen_s=0.01)
    assert r.ok
    assert pulses == []
    assert any("deasserted" in ln for ln in r.lines)
    assert any("knocks this attempt" in ln for ln in r.lines)


def test_probe_auto_falls_back_to_pulse(monkeypatch):
    fake = _FakeSer()
    pulses: list[int] = []
    listens = {"n": 0}

    def _listen(_s, _t, **_k):
        listens["n"] += 1
        if listens["n"] == 1:
            return b"", 2
        return b"fw_name=XUSSC fw_version=0.0.1\n", 1

    _install_fake_serial(monkeypatch, fake)
    monkeypatch.setattr(mod, "_pulse_reset", lambda _s: pulses.append(1))
    monkeypatch.setattr(mod, "_listen_with_knock_retries", _listen)
    monkeypatch.setattr(mod.time, "sleep", lambda *_: None)

    r = probe_serial_identity("COM7", reset=None, listen_s=0.01, boot_wait_s=0.0)
    assert r.ok
    assert pulses == [1]
    assert any("Pulse DTR/RTS" in ln for ln in r.lines)


def test_probe_empty_reports_ch9102_hint(monkeypatch):
    fake = _FakeSer()
    _install_fake_serial(monkeypatch, fake)
    monkeypatch.setattr(
        mod, "_listen_with_knock_retries", lambda _s, _t, **_k: (b"", 3)
    )
    monkeypatch.setattr(mod.time, "sleep", lambda *_: None)

    r = probe_serial_identity("COM7", reset=False, listen_s=0.01)
    assert not r.ok
    assert any("CH9102" in ln for ln in r.lines)
    assert any("answer identity on the link" in ln for ln in r.lines)


def test_listen_with_knock_retries_reknocks_until_identity(monkeypatch):
    """Shipped retry path: first reads empty, later knock sees identity (#79)."""
    fake = _FakeSer()
    knocks = {"n": 0}

    def _knock(_s):
        knocks["n"] += 1

    def _read(_size=1):
        if knocks["n"] >= 3:
            return b"fw_name=XUSSC fw_version=0.0.1\n"
        return b""

    fake.read = _read
    monkeypatch.setattr(mod, "_knock_once", _knock)
    t = {"now": 0.0}

    def _time():
        return t["now"]

    def _sleep(dt):
        t["now"] += float(dt)

    monkeypatch.setattr(mod.time, "time", _time)
    monkeypatch.setattr(mod.time, "sleep", _sleep)

    raw, n = mod._listen_with_knock_retries(
        fake, listen_s=2.0, knock=True, knock_interval_s=0.4
    )
    assert b"fw_name=XUSSC" in raw
    assert n >= 3
    assert knocks["n"] >= 3


def test_open_port_busy_hint(monkeypatch):
    class _Busy:
        def __init__(self):
            self.port = None
            self.baudrate = 0
            self.timeout = 0
            self.write_timeout = 0
            self.dtr = False
            self.rts = False

        def open(self):
            raise OSError("Access is denied.")

    class _SerialMod:
        Serial = staticmethod(lambda: _Busy())

    monkeypatch.setitem(__import__("sys").modules, "serial", _SerialMod)
    r = probe_serial_identity("COM7", listen_s=0.01)
    assert not r.ok
    assert any("port may be held" in ln.lower() or "HINT" in ln for ln in r.lines)
