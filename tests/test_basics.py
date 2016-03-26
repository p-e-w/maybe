from common import maybe


def test_noargs():
    assert "Error: No command given." in maybe("")
