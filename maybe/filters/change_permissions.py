# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from maybe import SyscallFilter, SYSCALL_FILTERS, T, get_full_path
from maybe.filters.create_write_file import get_file_descriptor_path


def format_permissions(permissions):
    result = ""
    for i in range(2, -1, -1):
        result += "r" if permissions & (4 * 8**i) else "-"
        result += "w" if permissions & (2 * 8**i) else "-"
        result += "x" if permissions & (1 * 8**i) else "-"
    return result


def format_change_permissions(path, permissions):
    return "%s of %s to %s" % (T.yellow("change permissions"), T.underline(path),
                               T.bold(format_permissions(permissions)))


SYSCALL_FILTERS["change_permissions"] = [
    SyscallFilter(
        syscall="chmod",
        format=lambda pid, args: format_change_permissions(get_full_path(pid, args[0]), args[1]),
    ),
    SyscallFilter(
        syscall="fchmod",
        format=lambda pid, args: format_change_permissions(get_file_descriptor_path(args[0]), args[1]),
    ),
    SyscallFilter(
        syscall="fchmodat",
        format=lambda pid, args: format_change_permissions(get_full_path(pid, args[1], args[0]), args[2]),
    ),
]
