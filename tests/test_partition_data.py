"""[[deploy.data]] partition resolve + plan (#79)."""

from __future__ import annotations

from pathlib import Path

from silico.partition_data import (
    parse_offset,
    parse_partitions_csv,
    plan_data_lines,
    read_deploy_data_specs,
    resolve_data_assets,
)
from silico.deploy_idf import plan_idf_deploy


CSV = """\
# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     0x9000,  0x6000,
factory,  app,  factory, 0x10000, 0x1F0000,
storage,  data, spiffs,  0x210000,0xF0000,
"""


def test_parse_partitions_csv_offsets():
    table = parse_partitions_csv(CSV)
    assert table["storage"] == 0x210000
    assert table["factory"] == 0x10000


def test_parse_offset_hex_and_dec():
    assert parse_offset("0x210000") == 0x210000
    assert parse_offset(0x1000) == 0x1000
    assert parse_offset("4096") == 4096


def test_resolve_data_assets_from_partition_name(tmp_path: Path):
    (tmp_path / "firmware").mkdir()
    (tmp_path / "firmware" / "partitions.csv").write_text(CSV, encoding="utf-8")
    assets = tmp_path / "assets"
    assets.mkdir()
    blob = assets / "song.raw"
    blob.write_bytes(b"\x00" * 100)
    (tmp_path / "silico.toml").write_text(
        """
[runtime]
language = "c"
chip = "esp32"
[deploy]
mode = "idf-flash"
project = "firmware"
[[deploy.data]]
name = "song"
file = "assets/song.raw"
partition = "storage"
""",
        encoding="utf-8",
    )
    specs = read_deploy_data_specs(tmp_path)
    assert len(specs) == 1
    resolved, errs = resolve_data_assets(tmp_path, specs)
    assert errs == []
    assert len(resolved) == 1
    assert resolved[0].offset == 0x210000
    assert resolved[0].size == 100
    lines = plan_data_lines(resolved, port="COM7")
    joined = "\n".join(lines)
    assert "0x210000" in joined
    assert "song" in joined


def test_plan_idf_includes_data_partition(tmp_path: Path, monkeypatch):
    import silico.deploy_idf as m
    from silico.ports import PortInfo

    (tmp_path / "firmware").mkdir()
    (tmp_path / "firmware" / "partitions.csv").write_text(CSV, encoding="utf-8")
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "song.raw").write_bytes(b"\x11" * 50)
    (tmp_path / "silico.toml").write_text(
        """
[runtime]
language = "c"
chip = "esp32"
toolchain = "esp-idf"
[deploy]
mode = "idf-flash"
project = "firmware"
[[deploy.data]]
name = "song"
file = "assets/song.raw"
partition = "storage"
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        m,
        "pick_best_port",
        lambda p: PortInfo(
            device=p,
            vid=None,
            pid=None,
            description="fake",
            manufacturer="",
            score=10,
            label="fake",
        ),
    )
    monkeypatch.setattr(m, "port_is_listed", lambda _p: True)
    monkeypatch.setattr(m, "idf_py_available", lambda: True)

    planned = plan_idf_deploy(port="COM7", root=tmp_path)
    assert not isinstance(planned, m.DeployResult)
    assert planned.kind == "idf"
    assert planned.data_assets
    assert planned.data_assets[0][0] == "song"
    assert planned.data_assets[0][2] == 0x210000
    joined = "\n".join(planned.lines)
    assert "Data partitions" in joined
    assert "0x210000" in joined
    assert "--yes" in joined
