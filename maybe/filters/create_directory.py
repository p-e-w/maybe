# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from maybe import SyscallFilter, SYSCALL_FILTERS, T, full_path


def format_create_directory(path):
    return "%s %s" % (T.cyan("create directory"), T.underline(path))


SYSCALL_FILTERS["create_directory"] = [
    SyscallFilter(
        syscall="mkdir",
        format=lambda pid, args: format_create_directory(full_path(pid, args[0])),
    ),
    SyscallFilter(
        syscall="mkdirat",
        format=lambda pid, args: format_create_directory(full_path(pid, args[1], args[0])),
    ),
]
