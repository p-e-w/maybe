# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from os.path import abspath

from maybe import SyscallFilter, SYSCALL_FILTERS, T


def format_delete(path):
    return "%s %s" % (T.red("delete"), T.underline(abspath(path)))


SYSCALL_FILTERS["delete"] = [
    SyscallFilter(
        name="unlink",
        signature=("int", (("const char *", "pathname"),)),
        format=lambda args: format_delete(args[0]),
    ),
    SyscallFilter(
        name="unlinkat",
        signature=("int", (("int", "dirfd"), ("const char *", "pathname"), ("int", "flags"),)),
        format=lambda args: format_delete(args[1]),
    ),
    SyscallFilter(
        name="rmdir",
        signature=("int", (("const char *", "pathname"),)),
        format=lambda args: format_delete(args[0]),
    ),
]
