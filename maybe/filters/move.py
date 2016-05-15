# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from os.path import dirname, basename

from maybe import T, register_filter, full_path


def filter_move(path_old, path_new):
    if dirname(path_old) == dirname(path_new):
        label = "rename"
        path_new = basename(path_new)
    else:
        label = "move"
    return "%s %s to %s" % (T.green(label), T.underline(path_old), T.underline(path_new)), 0


filter_scope = "move"

register_filter(filter_scope, "rename", lambda pid, args:
                filter_move(full_path(pid, args[0]), full_path(pid, args[1])))
register_filter(filter_scope, "renameat", lambda pid, args:
                filter_move(full_path(pid, args[1], args[0]), full_path(pid, args[3], args[2])))
register_filter(filter_scope, "renameat2", lambda pid, args:
                filter_move(full_path(pid, args[1], args[0]), full_path(pid, args[3], args[2])))
