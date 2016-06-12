from common import tf


def test_delete_file(tmpdir):
    tf(tmpdir, "rm '{f}'", "delete {f}", "delete", lambda f: f.check())
