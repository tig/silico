from silico.identity import Identity, match_expected, parse_identity_blob


def test_parse_kv_line():
    got = parse_identity_blob("fw_name=XUSSC fw_version=0.0.1\r\n")
    assert got is not None
    assert got.fw_name == "XUSSC"
    assert got.fw_version == "0.0.1"
    assert got.complete


def test_parse_two_line():
    got = parse_identity_blob("GCU\n0.0.1\n")
    assert got is not None
    assert got.fw_name == "GCU"
    assert got.fw_version == "0.0.1"


def test_parse_noise():
    assert parse_identity_blob("noise only\n") is None
    assert parse_identity_blob("") is None


def test_match_expected():
    idn = Identity("XUSSC", "0.0.1")
    assert match_expected(idn, expect_name="XUSSC", expect_version="0.0.1") == []
    fails = match_expected(idn, expect_name="OTHER", expect_version="0.0.1")
    assert fails and "fw_name" in fails[0]
