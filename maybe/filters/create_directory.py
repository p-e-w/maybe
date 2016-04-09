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


def format_create_directory(path):
    return "%s %s" % (T.cyan("create directory"), T.underline(abspath(path)))


SYSCALL_FILTERS["create_directory"] = [
    SyscallFilter(
        name="mkdir",
        signature=("int", (("const char *", "pathname"), ("mode_t", "mode"),)),
        format=lambda args: format_create_directory(args[0]),
    ),
    SyscallFilter(
        name="mkdirat",
        signature=("int", (("int", "dirfd"), ("const char *", "pathname"), ("mode_t", "mode"),)),
        format=lambda args: format_create_directory(args[1]),
    ),
]
