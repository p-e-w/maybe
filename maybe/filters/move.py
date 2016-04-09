# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from os.path import abspath, dirname, basename

from maybe import SyscallFilter, SYSCALL_FILTERS, T


def format_move(path_old, path_new):
    path_old = abspath(path_old)
    path_new = abspath(path_new)
    if dirname(path_old) == dirname(path_new):
        label = "rename"
        path_new = basename(path_new)
    else:
        label = "move"
    return "%s %s to %s" % (T.green(label), T.underline(path_old), T.underline(path_new))


SYSCALL_FILTERS["move"] = [
    SyscallFilter(
        name="rename",
        signature=("int", (("const char *", "oldpath"), ("const char *", "newpath"),)),
        format=lambda args: format_move(args[0], args[1]),
    ),
    SyscallFilter(
        name="renameat",
        signature=("int", (("int", "olddirfd"), ("const char *", "oldpath"),
                           ("int", "newdirfd"), ("const char *", "newpath"),)),
        format=lambda args: format_move(args[1], args[3]),
    ),
    SyscallFilter(
        name="renameat2",
        signature=("int", (("int", "olddirfd"), ("const char *", "oldpath"),
                           ("int", "newdirfd"), ("const char *", "newpath"), ("unsigned int", "flags"),)),
        format=lambda args: format_move(args[1], args[3]),
    ),
]
