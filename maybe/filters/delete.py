# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from maybe import T, register_filter, full_path


def filter_delete(path):
    return "%s %s" % (T.red("delete"), T.underline(path)), 0


filter_scope = "delete"

register_filter(filter_scope, "unlink", lambda pid, args: filter_delete(full_path(pid, args[0])))
register_filter(filter_scope, "unlinkat", lambda pid, args: filter_delete(full_path(pid, args[1], args[0])))
register_filter(filter_scope, "rmdir", lambda pid, args: filter_delete(full_path(pid, args[0])))
