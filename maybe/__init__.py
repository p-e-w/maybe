# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from os import readlink
from os.path import join
from collections import namedtuple

from blessings import Terminal
from ptrace.syscall.posix_arg import AT_FDCWD


SyscallFilter = namedtuple("SyscallFilter", ["syscall", "format", "substitute"])
# Make returning zero the default substitute function
# Source: http://stackoverflow.com/a/18348004
SyscallFilter.__new__.__defaults__ = (lambda pid, args: 0,)


SYSCALL_FILTERS = {}


T = Terminal()


def initialize_terminal(style_output):
    # This hack works around two issues:
    # 1. The global object T is imported into the context of other modules,
    #    so (re)assigning T here has no effect.
    # 2. Setting T._does_styling to True does not call setupterm, resulting in
    #    an error unless styling was already enabled anyway.
    # Invoking the constructor manually keeps the imported references valid
    # and calls setupterm (again) if necessary.
    T.__init__(force_styling={
        "yes": True,
        "no": None,
        "auto": False,
    }[style_output])


# Start with a large number to avoid collisions with other FDs
next_file_descriptor = 1000000
file_descriptors = {}


def register_path(pid, path, file_descriptor=None):
    if file_descriptor is None:
        global next_file_descriptor
        file_descriptor = next_file_descriptor
        next_file_descriptor += 1
    file_descriptors[file_descriptor] = path
    return file_descriptor


def is_tracked_descriptor(pid, file_descriptor):
    return file_descriptor in file_descriptors


def descriptor_path(pid, file_descriptor):
    if file_descriptor in file_descriptors:
        return file_descriptors[file_descriptor]
    else:
        return readlink("/proc/%d/fd/%d" % (pid, file_descriptor))


# Implements the path resolution logic of the "*at" syscalls
def full_path(pid, path, directory_descriptor=AT_FDCWD):
    if directory_descriptor == AT_FDCWD:
        # Current working directory
        directory = readlink("/proc/%d/cwd" % pid)
    else:
        # Directory referred to by directory_descriptor
        directory = descriptor_path(pid, directory_descriptor)
    # Note that join will discard directory if path is absolute, as desired
    return join(directory, path)
