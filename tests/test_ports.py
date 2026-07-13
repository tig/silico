from silico.ports import PortInfo, _score, pick_best_port


def test_rp2_scores_high():
    score, label = _score(0x2E8A, 0x0005)
    assert score >= 100
    assert "RP2040" in label or "MicroPython" in label


def test_ch340_demoted():
    score, label = _score(0x1A86, 0x7523)
    assert score < 0
    assert "CH340" in label


def test_debug_probe_demoted():
    score, _ = _score(0x2E8A, 0x000C)
    assert score < 0


def test_pick_best_honors_explicit(monkeypatch):
    import silico.ports as ports

    monkeypatch.setattr(
        ports,
        "list_scored_ports",
        lambda: [
            PortInfo("COM3", 0x1A86, 0x7523, "ch", "m", -20, "CH340"),
            PortInfo("COM6", 0x2E8A, 0x0005, "rp", "m", 100, "RP"),
        ],
    )
    chosen = pick_best_port("COM3")
    assert chosen is not None
    assert chosen.device == "COM3"


def test_pick_best_refuses_low_score_only(monkeypatch):
    import silico.ports as ports

    monkeypatch.setattr(
        ports,
        "list_scored_ports",
        lambda: [PortInfo("COM3", 0x1A86, 0x7523, "ch", "m", -20, "CH340")],
    )
    assert pick_best_port(None) is None
