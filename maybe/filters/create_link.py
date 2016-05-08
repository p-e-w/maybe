# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from maybe import SyscallFilter, SYSCALL_FILTERS, T, get_full_path


def format_create_link(path_source, path_target, symbolic):
    label = "create symbolic link" if symbolic else "create hard link"
    return "%s from %s to %s" % (T.cyan(label), T.underline(path_source), T.underline(path_target))


SYSCALL_FILTERS["create_link"] = [
    SyscallFilter(
        syscall="link",
        format=lambda pid, args: format_create_link(get_full_path(pid, args[1]),
                                                    get_full_path(pid, args[0]), False),
    ),
    SyscallFilter(
        syscall="linkat",
        format=lambda pid, args: format_create_link(get_full_path(pid, args[3], args[2]),
                                                    get_full_path(pid, args[1], args[0]), False),
    ),
    SyscallFilter(
        syscall="symlink",
        format=lambda pid, args: format_create_link(get_full_path(pid, args[1]),
                                                    get_full_path(pid, args[0]), True),
    ),
    SyscallFilter(
        syscall="symlinkat",
        format=lambda pid, args: format_create_link(get_full_path(pid, args[2], args[1]),
                                                    get_full_path(pid, args[0]), True),
    ),
]
