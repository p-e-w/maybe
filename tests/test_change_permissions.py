from os import access, X_OK

from common import tf


def test_change_permissions_file(tmpdir):
    tf(tmpdir, "chmod +x '{f}'", "change permissions of {f} to rwxr-xr-x",
       "change_permissions", lambda f: not access(str(f), X_OK))
