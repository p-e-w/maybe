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
        syscall="rename",
        format=lambda pid, args: format_move(args[0], args[1]),
    ),
    SyscallFilter(
        syscall="renameat",
        format=lambda pid, args: format_move(args[1], args[3]),
    ),
    SyscallFilter(
        syscall="renameat2",
        format=lambda pid, args: format_move(args[1], args[3]),
    ),
]
