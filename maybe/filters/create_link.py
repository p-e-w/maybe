# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from maybe import T, register_filter, full_path


def filter_create_link(path_source, path_target, symbolic):
    label = "create symbolic link" if symbolic else "create hard link"
    return "%s from %s to %s" % (T.cyan(label), T.underline(path_source), T.underline(path_target)), 0


filter_scope = "create_link"

register_filter(filter_scope, "link", lambda pid, args:
                filter_create_link(full_path(pid, args[1]), full_path(pid, args[0]), False))
register_filter(filter_scope, "linkat", lambda pid, args:
                filter_create_link(full_path(pid, args[3], args[2]), full_path(pid, args[1], args[0]), False))
register_filter(filter_scope, "symlink", lambda pid, args:
                filter_create_link(full_path(pid, args[1]), full_path(pid, args[0]), True))
register_filter(filter_scope, "symlinkat", lambda pid, args:
                filter_create_link(full_path(pid, args[2], args[1]), full_path(pid, args[0]), True))
