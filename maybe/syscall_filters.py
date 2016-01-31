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
from collections import namedtuple
from os import O_WRONLY, O_RDWR, O_APPEND, O_CREAT, O_TRUNC
from os.path import abspath, dirname, basename, exists

from .utilities import T, format_permissions


def return_zero(args):
    return 0


def format_delete(path):
    return "%s %s" % (T.red("delete"), T.underline(abspath(path)))


def format_move(path_old, path_new):
    path_old = abspath(path_old)
    path_new = abspath(path_new)
    if dirname(path_old) == dirname(path_new):
        label = "rename"
        path_new = basename(path_new)
    else:
        label = "move"
    return "%s %s to %s" % (T.green(label), T.underline(path_old), T.underline(path_new))


def format_change_permissions(path, permissions):
    return "%s of %s to %s" % (T.yellow("change permissions"), T.underline(abspath(path)),
                               T.bold(format_permissions(permissions)))


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
    return "%s of %s to %s" % (T.yellow(label), T.underline(abspath(path)), T.bold(owner))


def format_create_directory(path):
    return "%s %s" % (T.cyan("create directory"), T.underline(abspath(path)))


def format_create_link(path_source, path_target, symbolic):
    label = "create symbolic link" if symbolic else "create hard link"
    return "%s from %s to %s" % (T.cyan(label), T.underline(abspath(path_source)), T.underline(abspath(path_target)))


# Start with a large number to avoid collisions with other FDs
# TODO: This approach is extremely brittle!
next_file_descriptor = 1000
file_descriptors = {}


def get_next_file_descriptor():
    global next_file_descriptor
    file_descriptor = next_file_descriptor
    next_file_descriptor += 1
    return file_descriptor


def get_file_descriptor_path(file_descriptor):
    return file_descriptors.get(file_descriptor, "/dev/fd/%d" % file_descriptor)


def format_open(path, flags):
    path = abspath(path)
    if (flags & O_CREAT) and not exists(path):
        return "%s %s" % (T.cyan("create file"), T.underline(path))
    elif (flags & O_TRUNC) and exists(path):
        return "%s %s" % (T.red("truncate file"), T.underline(path))
    else:
        return None


def substitute_open(path, flags):
    path = abspath(path)
    if path == "/dev/tty":
        # Allow full access to terminal device
        return None
    elif (flags & O_WRONLY) or (flags & O_RDWR) or (flags & O_APPEND) or (format_open(path, flags) is not None):
        # File might be written to later, so we need to track the file descriptor
        file_descriptor = get_next_file_descriptor()
        file_descriptors[file_descriptor] = path
        return file_descriptor
    else:
        return None


def format_write(file_descriptor, byte_count):
    if file_descriptor in file_descriptors:
        path = file_descriptors[file_descriptor]
        return "%s %s to %s" % (T.red("write"), T.bold("%d bytes" % byte_count), T.underline(path))
    else:
        return None


def substitute_write(file_descriptor, byte_count):
    return None if (format_write(file_descriptor, byte_count) is None) else byte_count


def substitute_dup(file_descriptor_old, file_descriptor_new=None):
    if file_descriptor_old in file_descriptors:
        if file_descriptor_new is None:
            file_descriptor_new = get_next_file_descriptor()
        # Copy tracked file descriptor
        file_descriptors[file_descriptor_new] = file_descriptors[file_descriptor_old]
        return file_descriptor_new
    else:
        return None


SyscallFilter = namedtuple("SyscallFilter", ["name", "signature", "format", "substitute"])

SYSCALL_FILTERS = [
# Delete
SyscallFilter(
    name="remove",
    signature=("int", (("const char *", "pathname"),)),
    format=lambda args: format_delete(args[0]),
    substitute=return_zero
),
SyscallFilter(
    name="unlink",
    signature=("int", (("const char *", "pathname"),)),
    format=lambda args: format_delete(args[0]),
    substitute=return_zero
),
SyscallFilter(
    name="unlinkat",
    signature=("int", (("int", "dirfd"), ("const char *", "pathname"), ("int", "flags"),)),
    format=lambda args: format_delete(args[1]),
    substitute=return_zero
),
SyscallFilter(
    name="rmdir",
    signature=("int", (("const char *", "pathname"),)),
    format=lambda args: format_delete(args[0]),
    substitute=return_zero
),
# Move
SyscallFilter(
    name="rename",
    signature=("int", (("const char *", "oldpath"), ("const char *", "newpath"),)),
    format=lambda args: format_move(args[0], args[1]),
    substitute=return_zero
),
SyscallFilter(
    name="renameat",
    signature=("int", (("int", "olddirfd"), ("const char *", "oldpath"),
                       ("int", "newdirfd"), ("const char *", "newpath"),)),
    format=lambda args: format_move(args[1], args[3]),
    substitute=return_zero
),
SyscallFilter(
    name="renameat2",
    signature=("int", (("int", "olddirfd"), ("const char *", "oldpath"),
                       ("int", "newdirfd"), ("const char *", "newpath"), ("unsigned int", "flags"),)),
    format=lambda args: format_move(args[1], args[3]),
    substitute=return_zero
),
# Change permissions
SyscallFilter(
    name="chmod",
    signature=("int", (("const char *", "pathname"), ("mode_t", "mode"),)),
    format=lambda args: format_change_permissions(args[0], args[1]),
    substitute=return_zero
),
SyscallFilter(
    name="fchmod",
    signature=("int", (("int", "fd"), ("mode_t", "mode"),)),
    format=lambda args: format_change_permissions(get_file_descriptor_path(args[0]), args[1]),
    substitute=return_zero
),
SyscallFilter(
    name="fchmodat",
    signature=("int", (("int", "dirfd"), ("const char *", "pathname"), ("mode_t", "mode"), ("int", "flags"),)),
    format=lambda args: format_change_permissions(args[1], args[2]),
    substitute=return_zero
),
# Change owner
SyscallFilter(
    name="chown",
    signature=("int", (("const char *", "pathname"), ("uid_t", "owner"), ("gid_t", "group"),)),
    format=lambda args: format_change_owner(args[0], args[1], args[2]),
    substitute=return_zero
),
SyscallFilter(
    name="fchown",
    signature=("int", (("int", "fd"), ("uid_t", "owner"), ("gid_t", "group"),)),
    format=lambda args: format_change_owner(get_file_descriptor_path(args[0]), args[1], args[2]),
    substitute=return_zero
),
SyscallFilter(
    name="lchown",
    signature=("int", (("const char *", "pathname"), ("uid_t", "owner"), ("gid_t", "group"),)),
    format=lambda args: format_change_owner(args[0], args[1], args[2]),
    substitute=return_zero
),
SyscallFilter(
    name="fchownat",
    signature=("int", (("int", "dirfd"), ("const char *", "pathname"),
                       ("uid_t", "owner"), ("gid_t", "group"), ("int", "flags"),)),
    format=lambda args: format_change_owner(args[1], args[2], args[3]),
    substitute=return_zero
),
# Create directory
SyscallFilter(
    name="mkdir",
    signature=("int", (("const char *", "pathname"), ("mode_t", "mode"),)),
    format=lambda args: format_create_directory(args[0]),
    substitute=return_zero
),
SyscallFilter(
    name="mkdirat",
    signature=("int", (("int", "dirfd"), ("const char *", "pathname"), ("mode_t", "mode"),)),
    format=lambda args: format_create_directory(args[1]),
    substitute=return_zero
),
# Create link
SyscallFilter(
    name="link",
    signature=("int", (("const char *", "oldpath"), ("const char *", "newpath"),)),
    format=lambda args: format_create_link(args[1], args[0], False),
    substitute=return_zero
),
SyscallFilter(
    name="linkat",
    signature=("int", (("int", "olddirfd"), ("const char *", "oldpath"),
                       ("int", "newdirfd"), ("const char *", "newpath"), ("int", "flags"),)),
    format=lambda args: format_create_link(args[3], args[1], False),
    substitute=return_zero
),
SyscallFilter(
    name="symlink",
    signature=("int", (("const char *", "target"), ("const char *", "linkpath"),)),
    format=lambda args: format_create_link(args[1], args[0], True),
    substitute=return_zero
),
SyscallFilter(
    name="symlinkat",
    signature=("int", (("const char *", "target"), ("int", "newdirfd"), ("const char *", "linkpath"),)),
    format=lambda args: format_create_link(args[2], args[0], True),
    substitute=return_zero
),
# Open/create file
SyscallFilter(
    name="open",
    # TODO: "open" is overloaded (a version with 3 arguments also exists). Are both handled properly?
    signature=("int", (("const char *", "pathname"), ("int", "flags"),)),
    format=lambda args: format_open(args[0], args[1]),
    substitute=lambda args: substitute_open(args[0], args[1])
),
SyscallFilter(
    name="creat",
    signature=("int", (("const char *", "pathname"), ("mode_t", "mode"),)),
    format=lambda args: format_open(args[0], O_CREAT | O_WRONLY | O_TRUNC),
    substitute=lambda args: substitute_open(args[0], O_CREAT | O_WRONLY | O_TRUNC)
),
SyscallFilter(
    name="openat",
    # TODO: "openat" is overloaded (see above)
    signature=("int", (("int", "dirfd"), ("const char *", "pathname"), ("int", "flags"),)),
    format=lambda args: format_open(args[1], args[2]),
    substitute=lambda args: substitute_open(args[1], args[2])
),
# Write to file
# TODO: Handle "fwrite"?
SyscallFilter(
    name="write",
    signature=("ssize_t", (("int", "fd"), ("const void *", "buf"), ("size_t", "count"),)),
    format=lambda args: format_write(args[0], args[2]),
    substitute=lambda args: substitute_write(args[0], args[2])
),
SyscallFilter(
    name="pwrite",
    signature=("ssize_t", (("int", "fd"), ("const void *", "buf"), ("size_t", "count"), ("off_t", "offset"),)),
    format=lambda args: format_write(args[0], args[2]),
    substitute=lambda args: substitute_write(args[0], args[2])
),
SyscallFilter(
    name="writev",
    signature=("ssize_t", (("int", "fd"), ("const struct iovec *", "iov"), ("int", "iovcnt"),)),
    # TODO: Actual byte count is iovcnt * iov.iov_len
    format=lambda args: format_write(args[0], args[2]),
    substitute=lambda args: substitute_write(args[0], args[2])
),
SyscallFilter(
    name="pwritev",
    signature=("ssize_t", (("int", "fd"), ("const struct iovec *", "iov"), ("int", "iovcnt"), ("off_t", "offset"),)),
    # TODO: Actual byte count is iovcnt * iov.iov_len
    format=lambda args: format_write(args[0], args[2]),
    substitute=lambda args: substitute_write(args[0], args[2])
),
# Duplicate file descriptor
SyscallFilter(
    name="dup",
    signature=("int", (("int", "oldfd"),)),
    format=lambda args: None,
    substitute=lambda args: substitute_dup(args[0])
),
SyscallFilter(
    name="dup2",
    signature=("int", (("int", "oldfd"), ("int", "newfd"),)),
    format=lambda args: None,
    substitute=lambda args: substitute_dup(args[0], args[1])
),
SyscallFilter(
    name="dup3",
    signature=("int", (("int", "oldfd"), ("int", "newfd"), ("int", "flags"),)),
    format=lambda args: None,
    substitute=lambda args: substitute_dup(args[0], args[1])
),
]
