import sys
import shlex

from six import StringIO

from maybe.maybe import main as maybe_main


def maybe(arguments):
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = string_io = StringIO()
    maybe_main(shlex.split(arguments))
    assert sys.stdout == sys.stderr == string_io
    sys.stdout, sys.stderr = old_stdout, old_stderr
    return string_io.getvalue().rstrip("\n")
