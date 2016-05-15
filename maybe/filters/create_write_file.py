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

from maybe import T, register_filter, register_path, is_tracked_descriptor, descriptor_path, full_path


allowed_files = set(["/dev/null", "/dev/zero", "/dev/tty"])


def filter_open(pid, path, flags):
    if path in allowed_files:
        return None, None
    if (flags & O_CREAT) and not exists(path):
        operation = "%s %s" % (T.cyan("create file"), T.underline(path))
    elif (flags & O_TRUNC) and exists(path):
        operation = "%s %s" % (T.red("truncate file"), T.underline(path))
    else:
        operation = None
    if (flags & O_WRONLY) or (flags & O_RDWR) or (flags & O_APPEND) or (operation is not None):
        # File might be written to later, so we need to track the file descriptor
        return_value = register_path(pid, path)
    else:
        return_value = None
    return operation, return_value


def filter_mknod(path, type):
    if exists(path):
        return None, None
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
    return "%s %s" % (T.cyan(label), T.underline(path)), 0


def filter_write(pid, file_descriptor, byte_count):
    if is_tracked_descriptor(pid, file_descriptor):
        path = descriptor_path(pid, file_descriptor)
        return "%s %s to %s" % (T.red("write"), T.bold("%d bytes" % byte_count), T.underline(path)), byte_count
    else:
        return None, None


def filter_dup(pid, file_descriptor_old, file_descriptor_new=None):
    if is_tracked_descriptor(pid, file_descriptor_old):
        # Copy tracked file descriptor
        return None, register_path(pid, descriptor_path(pid, file_descriptor_old), file_descriptor_new)
    else:
        return None, None


filter_scope = "create_write_file"

register_filter(filter_scope, "open", lambda pid, args: filter_open(pid, full_path(pid, args[0]), args[1]))
register_filter(filter_scope, "creat", lambda pid, args:
                filter_open(pid, full_path(pid, args[0]), O_CREAT | O_WRONLY | O_TRUNC))
register_filter(filter_scope, "openat", lambda pid, args: filter_open(pid, full_path(pid, args[1], args[0]), args[2]))
register_filter(filter_scope, "mknod", lambda pid, args: filter_mknod(full_path(pid, args[0]), args[1]))
register_filter(filter_scope, "mknodat", lambda pid, args: filter_mknod(full_path(pid, args[1], args[0]), args[2]))
register_filter(filter_scope, "write", lambda pid, args: filter_write(pid, args[0], args[2]))
register_filter(filter_scope, "pwrite", lambda pid, args: filter_write(pid, args[0], args[2]))
# TODO: Actual byte count is iovcnt * iov.iov_len
register_filter(filter_scope, "writev", lambda pid, args: filter_write(pid, args[0], args[2]))
register_filter(filter_scope, "pwritev", lambda pid, args: filter_write(pid, args[0], args[2]))
register_filter(filter_scope, "dup", lambda pid, args: filter_dup(pid, args[0]))
register_filter(filter_scope, "dup2", lambda pid, args: filter_dup(pid, args[0], args[1]))
register_filter(filter_scope, "dup3", lambda pid, args: filter_dup(pid, args[0], args[1]))
