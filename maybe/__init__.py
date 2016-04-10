# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from collections import namedtuple

from blessings import Terminal


SyscallFilter = namedtuple("SyscallFilter", ["name", "signature", "format", "substitute"])
# Make returning zero the default substitute function
# Source: http://stackoverflow.com/a/18348004
SyscallFilter.__new__.__defaults__ = (lambda args: 0,)


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
