import sys
import shlex

from six import PY2, StringIO

from maybe.maybe import main as maybe_main


def maybe(arguments):
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = string_io = StringIO()
    maybe_main(shlex.split(arguments))
    assert sys.stdout == sys.stderr == string_io
    sys.stdout, sys.stderr = old_stdout, old_stderr
    return string_io.getvalue().rstrip("\n")


def to_unicode(string):
    if PY2:
        return unicode(string, sys.getfilesystemencoding())  # noqa
    else:
        return string


def tf(directory, command, output, operation, test):
    def t_file(name):
        if PY2:
            name = name.encode(sys.getfilesystemencoding())
        f = directory.join(name)
        # File does not yet exist (will be created when written to)
        assert not f.check()
        f.write("abc")
        assert f.check()
        # Test for expected output and provided test condition
        assert maybe("-l -- " + command.format(f=f)) == to_unicode(output.format(f=f))
        assert test(f)
        # Test for negation of the above if operation is explicitly allowed
        assert maybe(("-l -a %s -- " % operation) + command.format(f=f)).startswith("maybe has not detected")
        assert not test(f)

    t_file("filename")
    # Whitespace in filename
    t_file("file name")
    # Unicode in filename
    t_file(u"file name \u2713")
