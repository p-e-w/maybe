# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from blessings import Terminal
from ptrace.os_tools import RUNNING_LINUX
from ptrace.cpu_info import CPU_POWERPC, CPU_ARM, CPU_I386, CPU_X86_64


T = Terminal()


def format_permissions(permissions):
    result = ""
    for i in range(2, -1, -1):
        result += "r" if permissions & (4 * 8**i) else "-"
        result += "w" if permissions & (2 * 8**i) else "-"
        result += "x" if permissions & (1 * 8**i) else "-"
    return result


# Based on python-ptrace's PtraceSyscall.readSyscall
def get_syscall_register():
    if CPU_POWERPC:
        return "gpr0"
    elif CPU_ARM:
        return "r7"
    elif RUNNING_LINUX:
        if CPU_X86_64:
            return "orig_rax"
        else:
            return "orig_eax"
    else:
        if CPU_X86_64:
            return "rax"
        else:
            return "eax"


# Based on python-ptrace's PtraceSyscall.exit
def get_return_value_register():
    if CPU_ARM:
        return "r0"
    elif CPU_I386:
        return "eax"
    elif CPU_X86_64:
        return "rax"
    elif CPU_POWERPC:
        return "result"
    else:
        raise NotImplementedError("Unsupported CPU architecture")


SYSCALL_REGISTER = get_syscall_register()
RETURN_VALUE_REGISTER = get_return_value_register()
