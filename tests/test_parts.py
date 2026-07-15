"""Part truth: parts.toml parsing, validation, and the local fetch cache."""

from pathlib import Path

from silico.parts import CACHE_DIR, fetch_parts, load_parts


def _write(tmp_path: Path, text: str) -> Path:
    (tmp_path / "parts.toml").write_text(text, encoding="utf-8")
    return tmp_path


VALID = """
[[part]]
id = "rp2040"
name = "Raspberry Pi RP2040"
role = "mcu"
datasheet = "https://example.com/rp2040.pdf"
svd = "https://example.com/RP2040.svd"
"""


def test_valid_parts_parse(tmp_path):
    report = load_parts(_write(tmp_path, VALID))
    assert report.ok
    assert report.parts[0].id == "rp2040"
    assert set(report.parts[0].pointers) == {"datasheet", "svd"}


def test_missing_file_is_info_not_failure(tmp_path):
    report = load_parts(tmp_path)
    assert report.ok and not report.parts
    assert any("no parts.toml" in l for l in report.lines)


def test_part_without_pointers_fails(tmp_path):
    report = load_parts(_write(tmp_path, '[[part]]\nid = "x"\nname = "X"\n'))
    assert not report.ok
    assert any("no truth pointer" in l for l in report.lines)


def test_non_url_pointer_fails(tmp_path):
    bad = '[[part]]\nid = "x"\nname = "X"\ndatasheet = "C:/docs/x.pdf"\n'
    report = load_parts(_write(tmp_path, bad))
    assert not report.ok
    assert any("not an http(s) URL" in l for l in report.lines)


def test_duplicate_id_fails(tmp_path):
    dup = VALID + '\n[[part]]\nid = "rp2040"\nname = "Again"\ndocs = "https://e.com/d"\n'
    report = load_parts(_write(tmp_path, dup))
    assert not report.ok


def test_fetch_writes_cache_and_skips_existing(tmp_path):
    root = _write(tmp_path, VALID)
    calls = []

    def fake_fetch(url):
        calls.append(url)
        return b"doc-bytes"

    report = fetch_parts(root, fetcher=fake_fetch)
    assert report.ok
    cached = root / CACHE_DIR / "rp2040" / "datasheet.pdf"
    assert cached.read_bytes() == b"doc-bytes"
    assert (root / CACHE_DIR / "rp2040" / "svd.svd").exists()
    assert len(calls) == 2

    # Second run: cache hit, no re-fetch.
    report2 = fetch_parts(root, fetcher=fake_fetch)
    assert report2.ok and len(calls) == 2
    assert any(l.startswith("cached:") for l in report2.lines)


def test_fetch_failure_reports_and_continues(tmp_path):
    root = _write(tmp_path, VALID)

    def flaky(url):
        if url.endswith(".pdf"):
            raise OSError("boom")
        return b"ok"

    report = fetch_parts(root, fetcher=flaky)
    assert not report.ok
    assert any("fetch failed" in l for l in report.lines)
    assert (root / CACHE_DIR / "rp2040" / "svd.svd").exists()


def test_plate_parts_toml_is_valid():
    from silico.scaffold import plate_root

    report = load_parts(plate_root())
    assert report.ok, "\n".join(report.lines)
    assert any(p.id == "rp2040" for p in report.parts)
