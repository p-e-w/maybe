# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016-2017 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from __future__ import unicode_literals, print_function

import sys
import subprocess
from imp import load_source
from ast import literal_eval
from argparse import ArgumentParser
from logging import getLogger, NullHandler
from os.path import splitext, basename

from six import PY2
from six.moves import input
from ptrace.tools import locateProgram
from ptrace.debugger import ProcessSignal, NewProcessEvent, ProcessExecution, ProcessExit
from ptrace.debugger.child import createChild
from ptrace.debugger.debugger import PtraceDebugger
from ptrace.func_call import FunctionCallOptions
from ptrace.syscall import SYSCALL_REGISTER, RETURN_VALUE_REGISTER, DIRFD_ARGUMENTS
from ptrace.syscall.posix_constants import SYSCALL_ARG_DICT
from ptrace.syscall.syscall_argument import ARGUMENT_CALLBACK

from . import SYSCALL_FILTERS, T, initialize_terminal
from .process import Process
# Filter modules are imported not to use them as symbols, but to execute their top-level code
from .filters import (delete, move, change_permissions, change_owner,    # noqa
                      create_directory, create_link, create_write_file)  # noqa


def parse_argument(argument):
    # createText() uses repr() to render the argument,
    # for which literal_eval() acts as an inverse function
    # (see http://stackoverflow.com/a/24886425)
    argument = literal_eval(argument.createText())
    if PY2 and isinstance(argument, str):
        argument = unicode(argument, sys.getfilesystemencoding())  # noqa
    return argument


def get_operations(debugger, syscall_filters, verbose):
    format_options = FunctionCallOptions(
        replace_socketcall=False,
        string_max_length=4096,
    )

    processes = {}
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
            event.process.syscall()
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
            if syscall.name in syscall_filters:
                if verbose == 1:
                    print(syscall.format())
                elif verbose == 2:
                    print(T.bold(syscall.format()))

                filter_function = syscall_filters[syscall.name]
                if process.pid not in processes:
                    processes[process.pid] = Process(process)
                arguments = [parse_argument(argument) for argument in syscall.arguments]

                operation, return_value = filter_function(processes[process.pid], arguments)

                if operation is not None:
                    operations.append(operation)

                if return_value is not None:
                    # Set invalid syscall number to prevent call execution
                    process.setreg(SYSCALL_REGISTER, -1)
                    # Substitute return value to make syscall appear to have succeeded
                    process.setreg(RETURN_VALUE_REGISTER, return_value)

            elif verbose == 2:
                print(syscall.format())

        process.syscall()

    return operations


def main(argv=sys.argv[1:]):
    if PY2:
        argv = [unicode(arg, sys.getfilesystemencoding()) for arg in argv]  # noqa

    # Insert positional argument separator, if not already present
    if "--" not in argv:
        for i, argument in enumerate(argv):
            if not argument.startswith("-"):
                argv.insert(i, "--")
                break

    arg_parser = ArgumentParser(
        prog="maybe",
        usage="%(prog)s [options] command [argument ...]",
        description="Run a command without the ability to make changes to your system " +
                    "and list the changes it would have made.",
        epilog="For more information, to report issues or to contribute, " +
               "visit https://github.com/p-e-w/maybe.",
    )
    arg_parser.add_argument("command", nargs="+", help="the command to run under maybe's control")
    arg_group = arg_parser.add_mutually_exclusive_group()
    arg_group.add_argument("-a", "--allow", nargs="+", metavar="OPERATION",
                           help="allow the command to perform the specified operation(s). " +
                                "all other operations will be denied. " +
                                "possible values for %(metavar)s are: " +
                                ", ".join(sorted(SYSCALL_FILTERS.keys())) +
                                "; as well as any filter scopes defined by loaded plugins")
    arg_group.add_argument("-d", "--deny", nargs="+", metavar="OPERATION",
                           help="deny the command the specified operation(s). " +
                                "all other operations will be allowed. " +
                                "see --allow for a list of possible values for %(metavar)s. " +
                                "--allow and --deny cannot be combined")
    arg_parser.add_argument("-p", "--plugin", nargs="+", metavar="FILE",
                            help="load the specified plugin script(s). " +
                                 "see the README for details and plugin API documentation")
    arg_parser.add_argument("-l", "--list-only", action="store_true",
                            help="list operations without header, indentation and rerun prompt")
    arg_parser.add_argument("--style-output", choices=["yes", "no", "auto"], default="auto",
                            help="colorize output using ANSI escape sequences (yes/no) " +
                                 "or automatically decide based on whether stdout is a terminal (auto, default)")
    arg_parser.add_argument("-v", "--verbose", action="count",
                            help="if specified once, print every filtered syscall. " +
                                 "if specified twice, print every syscall, highlighting filtered syscalls")
    arg_parser.add_argument("--version", action="version", version="%(prog)s 0.4.0")
    args = arg_parser.parse_args(argv)

    initialize_terminal(args.style_output)

    if args.plugin is not None:
        for plugin_path in args.plugin:
            try:
                module_name = splitext(basename(plugin_path))[0]
                # Note: imp.load_source is *long* deprecated and not even documented
                # in Python 3 anymore, but it still seems to work and the "alternatives"
                # (see http://stackoverflow.com/a/67692) are simply too insane to use
                load_source(module_name, plugin_path)
            except Exception as error:
                print(T.red("Error loading %s: %s." % (T.bold(plugin_path) + T.red, error)))
                return 1

    if args.allow is not None:
        for filter_scope in args.allow:
            if filter_scope not in SYSCALL_FILTERS:
                print(T.red("Unknown operation in --allow: %s." % (T.bold(filter_scope) + T.red)))
                return 1
        filter_scopes = set(SYSCALL_FILTERS.keys()) - set(args.allow)
    elif args.deny is not None:
        for filter_scope in args.deny:
            if filter_scope not in SYSCALL_FILTERS:
                print(T.red("Unknown operation in --deny: %s." % (T.bold(filter_scope) + T.red)))
                return 1
        filter_scopes = args.deny
    else:
        filter_scopes = SYSCALL_FILTERS.keys()

    syscall_filters = {}

    for filter_scope in SYSCALL_FILTERS:
        if filter_scope in filter_scopes:
            for syscall in SYSCALL_FILTERS[filter_scope]:
                syscall_filters[syscall] = SYSCALL_FILTERS[filter_scope][syscall]

    # Suppress logging output from python-ptrace
    getLogger().addHandler(NullHandler())

    # Prevent python-ptrace from decoding arguments to keep raw numerical values
    DIRFD_ARGUMENTS.clear()
    SYSCALL_ARG_DICT.clear()
    ARGUMENT_CALLBACK.clear()

    # This is basically "shlex.join"
    command = " ".join([(("'%s'" % arg) if (" " in arg) else arg) for arg in args.command])

    try:
        args.command[0] = locateProgram(args.command[0])
        pid = createChild(args.command, False)
    except Exception as error:
        print(T.red("Error executing %s: %s." % (T.bold(command) + T.red, error)))
        return 1

    debugger = PtraceDebugger()
    debugger.traceFork()
    debugger.traceExec()

    process = debugger.addProcess(pid, True)
    process.syscall()

    try:
        operations = get_operations(debugger, syscall_filters, args.verbose)
    except Exception as error:
        print(T.red("Error tracing process: %s." % error))
        return 1
    except KeyboardInterrupt:
        print(T.yellow("%s terminated by keyboard interrupt." % (T.bold(command) + T.yellow)))
        return 2
    finally:
        # Cut down all processes no matter what happens
        # to prevent them from doing any damage
        debugger.quit()

    if operations:
        if not args.list_only:
            print("%s has prevented %s from performing %d file system operations:\n" %
                  (T.bold("maybe"), T.bold(command), len(operations)))
        for operation in operations:
            print(("" if args.list_only else "  ") + operation)
        if not args.list_only:
            print("\nDo you want to rerun %s and permit these operations? [y/N] " % T.bold(command), end="")
            try:
                choice = input()
            except KeyboardInterrupt:
                choice = ""
                # Ctrl+C does not print a newline automatically
                print("")
            if choice.lower() == "y":
                subprocess.call(args.command)
    else:
        print("%s has not detected any file system operations from %s." %
              (T.bold("maybe"), T.bold(command)))
