# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from maybe import T, register_filter


def filter_create_directory(path):
    return "%s %s" % (T.cyan("create directory"), T.underline(path)), 0


filter_scope = "create_directory"

register_filter(filter_scope, "mkdir", lambda process, args:
                filter_create_directory(process.full_path(args[0])))
register_filter(filter_scope, "mkdirat", lambda process, args:
                filter_create_directory(process.full_path(args[1], args[0])))
