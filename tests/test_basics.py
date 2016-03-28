from common import maybe


def test_no_operations():
    assert maybe("true") == "maybe has not detected any file system operations from true."
