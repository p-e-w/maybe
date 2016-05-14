# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from os.path import exists
from os import O_WRONLY, O_RDWR, O_APPEND, O_CREAT, O_TRUNC
from stat import S_IFCHR, S_IFBLK, S_IFIFO, S_IFSOCK

from maybe import SyscallFilter, SYSCALL_FILTERS, T, register_path, is_tracked_descriptor, descriptor_path, full_path


allowed_files = set(["/dev/null", "/dev/zero", "/dev/tty"])


def format_open(path, flags):
    if path in allowed_files:
        return None
    elif (flags & O_CREAT) and not exists(path):
        return "%s %s" % (T.cyan("create file"), T.underline(path))
    elif (flags & O_TRUNC) and exists(path):
        return "%s %s" % (T.red("truncate file"), T.underline(path))
    else:
        return None


def substitute_open(pid, path, flags):
    if path in allowed_files:
        return None
    elif (flags & O_WRONLY) or (flags & O_RDWR) or (flags & O_APPEND) or (format_open(path, flags) is not None):
        # File might be written to later, so we need to track the file descriptor
        return register_path(pid, path)
    else:
        return None


def format_mknod(path, type):
    if exists(path):
        return None
    elif (type & S_IFCHR):
        label = "create character special file"
    elif (type & S_IFBLK):
        label = "create block special file"
    elif (type & S_IFIFO):
        label = "create named pipe"
    elif (type & S_IFSOCK):
        label = "create socket"
    else:
        # mknod(2): "Zero file type is equivalent to type S_IFREG"
        label = "create file"
    return "%s %s" % (T.cyan(label), T.underline(path))


def substitute_mknod(path, type):
    return None if (format_mknod(path, type) is None) else 0


def format_write(pid, file_descriptor, byte_count):
    if is_tracked_descriptor(pid, file_descriptor):
        path = descriptor_path(pid, file_descriptor)
        return "%s %s to %s" % (T.red("write"), T.bold("%d bytes" % byte_count), T.underline(path))
    else:
        return None


def substitute_write(pid, file_descriptor, byte_count):
    return None if (format_write(pid, file_descriptor, byte_count) is None) else byte_count


def substitute_dup(pid, file_descriptor_old, file_descriptor_new=None):
    if is_tracked_descriptor(pid, file_descriptor_old):
        # Copy tracked file descriptor
        return register_path(pid, descriptor_path(pid, file_descriptor_old), file_descriptor_new)
    else:
        return None


SYSCALL_FILTERS["create_write_file"] = [
    SyscallFilter(
        syscall="open",
        format=lambda pid, args: format_open(full_path(pid, args[0]), args[1]),
        substitute=lambda pid, args: substitute_open(pid, full_path(pid, args[0]), args[1]),
    ),
    SyscallFilter(
        syscall="creat",
        format=lambda pid, args: format_open(full_path(pid, args[0]), O_CREAT | O_WRONLY | O_TRUNC),
        substitute=lambda pid, args: substitute_open(pid, full_path(pid, args[0]), O_CREAT | O_WRONLY | O_TRUNC),
    ),
    SyscallFilter(
        syscall="openat",
        format=lambda pid, args: format_open(full_path(pid, args[1], args[0]), args[2]),
        substitute=lambda pid, args: substitute_open(pid, full_path(pid, args[1], args[0]), args[2]),
    ),
    SyscallFilter(
        syscall="mknod",
        format=lambda pid, args: format_mknod(full_path(pid, args[0]), args[1]),
        substitute=lambda pid, args: substitute_mknod(full_path(pid, args[0]), args[1]),
    ),
    SyscallFilter(
        syscall="mknodat",
        format=lambda pid, args: format_mknod(full_path(pid, args[1], args[0]), args[2]),
        substitute=lambda pid, args: substitute_mknod(full_path(pid, args[1], args[0]), args[2]),
    ),
    SyscallFilter(
        syscall="write",
        format=lambda pid, args: format_write(pid, args[0], args[2]),
        substitute=lambda pid, args: substitute_write(pid, args[0], args[2]),
    ),
    SyscallFilter(
        syscall="pwrite",
        format=lambda pid, args: format_write(pid, args[0], args[2]),
        substitute=lambda pid, args: substitute_write(pid, args[0], args[2]),
    ),
    SyscallFilter(
        syscall="writev",
        # TODO: Actual byte count is iovcnt * iov.iov_len
        format=lambda pid, args: format_write(pid, args[0], args[2]),
        substitute=lambda pid, args: substitute_write(pid, args[0], args[2]),
    ),
    SyscallFilter(
        syscall="pwritev",
        # TODO: Actual byte count is iovcnt * iov.iov_len
        format=lambda pid, args: format_write(pid, args[0], args[2]),
        substitute=lambda pid, args: substitute_write(pid, args[0], args[2]),
    ),
    SyscallFilter(
        syscall="dup",
        format=lambda pid, args: None,
        substitute=lambda pid, args: substitute_dup(pid, args[0]),
    ),
    SyscallFilter(
        syscall="dup2",
        format=lambda pid, args: None,
        substitute=lambda pid, args: substitute_dup(pid, args[0], args[1]),
    ),
    SyscallFilter(
        syscall="dup3",
        format=lambda pid, args: None,
        substitute=lambda pid, args: substitute_dup(pid, args[0], args[1]),
    ),
]
