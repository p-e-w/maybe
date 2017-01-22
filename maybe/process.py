# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016-2017 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from os import readlink
from os.path import normpath, join

from ptrace.syscall.posix_arg import AT_FDCWD


class Process(object):
    def __init__(self, ptrace_process):
        self._process = ptrace_process
        # Start with a large number to avoid collisions with other FDs
        self._next_file_descriptor = 1000000
        self._file_descriptors = {}

    def register_path(self, path, file_descriptor=None):
        if file_descriptor is None:
            file_descriptor = self._next_file_descriptor
            self._next_file_descriptor += 1
        self._file_descriptors[file_descriptor] = path
        return file_descriptor

    def is_tracked_descriptor(self, file_descriptor):
        return file_descriptor in self._file_descriptors

    def descriptor_path(self, file_descriptor):
        if file_descriptor in self._file_descriptors:
            path = self._file_descriptors[file_descriptor]
        else:
            path = readlink("/proc/%d/fd/%d" % (self._process.pid, file_descriptor))
        return normpath(path)

    # Implements the path resolution logic of the "*at" syscalls
    def full_path(self, path, directory_descriptor=AT_FDCWD):
        if directory_descriptor == AT_FDCWD:
            # Current working directory
            directory = readlink("/proc/%d/cwd" % self._process.pid)
        else:
            # Directory referred to by directory_descriptor
            directory = self.descriptor_path(directory_descriptor)
        # Note that join will discard directory if path is absolute, as desired
        return normpath(join(directory, path))
