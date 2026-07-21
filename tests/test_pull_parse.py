from silico.pull_device import _parse_ls_names


def test_parse_ls_size_prefixed():
    out = _parse_ls_names(
        """
ls :
         182 boot.py
       13089 main.py
           0 apps/
"""
    )
    assert "boot.py" in out
    assert "main.py" in out
    assert "apps" not in out


def test_parse_ls_skips_banner_noise():
    out = _parse_ls_names(
        """
MPY: soft reboot
>>> 
   120 version.py
"""
    )
    assert out == ["version.py"]
