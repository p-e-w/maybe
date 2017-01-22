# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016-2017 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from os.path import exists
from os import O_WRONLY, O_RDWR, O_APPEND, O_CREAT, O_TRUNC
from stat import S_IFCHR, S_IFBLK, S_IFIFO, S_IFSOCK

from maybe import T, register_filter


allowed_files = set(["/dev/null", "/dev/zero", "/dev/tty"])


def filter_open(process, path, flags):
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
        return_value = process.register_path(path)
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


def filter_write(process, file_descriptor, byte_count):
    if process.is_tracked_descriptor(file_descriptor):
        path = process.descriptor_path(file_descriptor)
        return "%s %s to %s" % (T.red("write"), T.bold("%d bytes" % byte_count), T.underline(path)), byte_count
    else:
        return None, None


def filter_dup(process, file_descriptor_old, file_descriptor_new=None):
    if process.is_tracked_descriptor(file_descriptor_old):
        # Copy tracked file descriptor
        return None, process.register_path(process.descriptor_path(file_descriptor_old), file_descriptor_new)
    else:
        return None, None


register_filter("open", lambda process, args:
                filter_open(process, process.full_path(args[0]), args[1]))
register_filter("creat", lambda process, args:
                filter_open(process, process.full_path(args[0]), O_CREAT | O_WRONLY | O_TRUNC))
register_filter("openat", lambda process, args:
                filter_open(process, process.full_path(args[1], args[0]), args[2]))
register_filter("mknod", lambda process, args:
                filter_mknod(process.full_path(args[0]), args[1]))
register_filter("mknodat", lambda process, args:
                filter_mknod(process.full_path(args[1], args[0]), args[2]))
register_filter("write", lambda process, args: filter_write(process, args[0], args[2]))
register_filter("pwrite", lambda process, args: filter_write(process, args[0], args[2]))
# TODO: Actual byte count is iovcnt * iov.iov_len
register_filter("writev", lambda process, args: filter_write(process, args[0], args[2]))
register_filter("pwritev", lambda process, args: filter_write(process, args[0], args[2]))
register_filter("dup", lambda process, args: filter_dup(process, args[0]))
register_filter("dup2", lambda process, args: filter_dup(process, args[0], args[1]))
register_filter("dup3", lambda process, args: filter_dup(process, args[0], args[1]))
