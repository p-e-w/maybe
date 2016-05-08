# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from pwd import getpwuid
from grp import getgrgid

from maybe import SyscallFilter, SYSCALL_FILTERS, T, get_full_path
from maybe.filters.create_write_file import get_file_descriptor_path


def format_change_owner(path, owner, group):
    if owner == -1:
        label = "change group"
        owner = getgrgid(group)[0]
    elif group == -1:
        label = "change owner"
        owner = getpwuid(owner)[0]
    else:
        label = "change owner"
        owner = getpwuid(owner)[0] + ":" + getgrgid(group)[0]
    return "%s of %s to %s" % (T.yellow(label), T.underline(path), T.bold(owner))


SYSCALL_FILTERS["change_owner"] = [
    SyscallFilter(
        syscall="chown",
        format=lambda pid, args: format_change_owner(get_full_path(pid, args[0]), args[1], args[2]),
    ),
    SyscallFilter(
        syscall="fchown",
        format=lambda pid, args: format_change_owner(get_file_descriptor_path(args[0]), args[1], args[2]),
    ),
    SyscallFilter(
        syscall="lchown",
        format=lambda pid, args: format_change_owner(get_full_path(pid, args[0]), args[1], args[2]),
    ),
    SyscallFilter(
        syscall="fchownat",
        format=lambda pid, args: format_change_owner(get_full_path(pid, args[1], args[0]), args[2], args[3]),
    ),
]
