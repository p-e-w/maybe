from os import access, X_OK

from common import tf, umask


def test_change_permissions_file(tmpdir):
    with umask(0o022):
        tf(tmpdir, "chmod +x '{f}'", "change permissions of {f} to rwxr-xr-x",
           "change_permissions", lambda f: not access(str(f), X_OK))
