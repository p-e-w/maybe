#!/usr/bin/env python

# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from sys import argv, exit
from subprocess import call

from ptrace.tools import locateProgram
from ptrace.debugger import ProcessSignal, NewProcessEvent, ProcessExecution, ProcessExit
from ptrace.debugger.child import createChild
from ptrace.debugger.debugger import PtraceDebugger, DebuggerError
from ptrace.func_call import FunctionCallOptions
from ptrace.syscall import SYSCALL_PROTOTYPES, FILENAME_ARGUMENTS
from ptrace.syscall.posix_constants import SYSCALL_ARG_DICT
from ptrace.syscall.syscall_argument import ARGUMENT_CALLBACK

from syscall_filters import SYSCALL_FILTERS
from utilities import T, SYSCALL_REGISTER, RETURN_VALUE_REGISTER


# Python 2/3 compatibility hack
# Source: http://stackoverflow.com/a/7321970
try:
    input = raw_input
except NameError:
    pass


# Register filtered syscalls with python-ptrace so they are parsed correctly
SYSCALL_PROTOTYPES.clear()
FILENAME_ARGUMENTS.clear()
for syscall_filter in SYSCALL_FILTERS:
    SYSCALL_PROTOTYPES[syscall_filter.name] = syscall_filter.signature
    for argument in syscall_filter.signature[1]:
        if argument[0] == "const char *":
            FILENAME_ARGUMENTS.add(argument[1])

# Turn list into dictionary indexed by syscall name for fast filter retrieval
SYSCALL_FILTERS = {syscall_filter.name: syscall_filter for syscall_filter in SYSCALL_FILTERS}

# Prevent python-ptrace from decoding arguments to keep raw numerical values
SYSCALL_ARG_DICT.clear()
ARGUMENT_CALLBACK.clear()


def prepareProcess(process):
    process.syscall()
    process.syscall_state.ignore_callback = lambda syscall: syscall.name not in SYSCALL_FILTERS


def parse_argument(argument):
    argument = argument.createText()
    if argument.startswith("'"):
        # Remove quotes from string argument
        return argument[1:-1]
    elif argument.startswith("b'"):
        # Python 3 bytes literal
        return argument[2:-1]
    else:
        # Note that "int" with base 0 infers the base from the prefix
        return int(argument, 0)


format_options = FunctionCallOptions(
    replace_socketcall=False,
    string_max_length=4096,
)


def get_operations(debugger):
    operations = []

    while True:
        if not debugger:
            # All processes have exited
            break

        # This logic is mostly based on python-ptrace's "strace" example
        try:
            syscall_event = debugger.waitSyscall()
        except ProcessSignal as event:
            event.process.syscall(event.signum)
            continue
        except NewProcessEvent as event:
            prepareProcess(event.process)
            event.process.parent.syscall()
            continue
        except ProcessExecution as event:
            event.process.syscall()
            continue
        except ProcessExit as event:
            continue

        process = syscall_event.process
        syscall_state = process.syscall_state

        syscall = syscall_state.event(format_options)

        if syscall and syscall_state.next_event == "exit":
            # Syscall is about to be executed (just switched from "enter" to "exit")
            syscall_filter = SYSCALL_FILTERS[syscall.name]

            arguments = [parse_argument(argument) for argument in syscall.arguments]

            operation = syscall_filter.format(arguments)
            if operation is not None:
                operations.append(operation)

            return_value = syscall_filter.substitute(arguments)
            if return_value is not None:
                # Set invalid syscall number to prevent call execution
                process.setreg(SYSCALL_REGISTER, -1)
                # Substitute return value to make syscall appear to have succeeded
                process.setreg(RETURN_VALUE_REGISTER, return_value)

        process.syscall()

    return operations


def main():
    if len(argv) < 2:
        print(T.red("Error: No command given."))
        print("Usage: %s COMMAND [ARGUMENT]..." % argv[0])
        exit(1)

    # This is basically "shlex.join"
    command = " ".join([(("'%s'" % arg) if (" " in arg) else arg) for arg in argv[1:]])

    arguments = argv[1:]
    arguments[0] = locateProgram(arguments[0])

    try:
        pid = createChild(arguments, False)
    except Exception as error:
        print(T.red("Error executing %s: %s." % (T.bold(command) + T.red, error)))
        exit(1)

    debugger = PtraceDebugger()
    debugger.traceExec()
    try:
        debugger.traceFork()
    except DebuggerError:
        print(T.yellow("Warning: Running without traceFork support. " +
                       "Syscalls from subprocesses can not be intercepted."))

    process = debugger.addProcess(pid, True)
    prepareProcess(process)

    try:
        operations = get_operations(debugger)
    except Exception as error:
        print(T.red("Error tracing process: %s." % error))
        exit(1)
    except KeyboardInterrupt:
        print(T.yellow("%s terminated by keyboard interrupt." % (T.bold(command) + T.yellow)))
        exit(2)
    finally:
        # Cut down all processes no matter what happens
        # to prevent them from doing any damage
        debugger.quit()

    if operations:
        print("%s has prevented %s from performing %d file system operations:\n" %
              (T.bold("maybe"), T.bold(command), len(operations)))
        for operation in operations:
            print("  " + operation)
        try:
            choice = input("\nDo you want to rerun %s and permit these operations? [y/N] " % T.bold(command))
        except KeyboardInterrupt:
            choice = ""
        if choice.lower() == "y":
            call(argv[1:])
    else:
        print("%s has not detected any file system operations from %s." %
              (T.bold("maybe"), T.bold(command)))


if __name__ == "__main__":
    main()
