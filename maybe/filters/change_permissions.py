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
from maybe.utilities import format_permissions
from maybe.filters.create_write_file import get_file_descriptor_path


def format_change_permissions(path, permissions):
    return "%s of %s to %s" % (T.yellow("change permissions"), T.underline(abspath(path)),
                               T.bold(format_permissions(permissions)))


SYSCALL_FILTERS["change_permissions"] = [
    SyscallFilter(
        name="chmod",
        signature=("int", (("const char *", "pathname"), ("mode_t", "mode"),)),
        format=lambda args: format_change_permissions(args[0], args[1]),
    ),
    SyscallFilter(
        name="fchmod",
        signature=("int", (("int", "fd"), ("mode_t", "mode"),)),
        format=lambda args: format_change_permissions(get_file_descriptor_path(args[0]), args[1]),
    ),
    SyscallFilter(
        name="fchmodat",
        signature=("int", (("int", "dirfd"), ("const char *", "pathname"), ("mode_t", "mode"), ("int", "flags"),)),
        format=lambda args: format_change_permissions(args[1], args[2]),
    ),
]
