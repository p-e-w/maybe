# maybe - see what a program does before deciding whether you really want it to happen
#
# Copyright (c) 2016-2017 Philipp Emanuel Weidmann <pew@worldwidemann.com>
#
# Nemo vir est qui mundum non reddat meliorem.
#
# Released under the terms of the GNU General Public License, version 3
# (https://gnu.org/licenses/gpl.html)


from maybe import T, register_filter


def filter_delete(path):
    return "%s %s" % (T.red("delete"), T.underline(path)), 0


register_filter("unlink", lambda process, args: filter_delete(process.full_path(args[0])))
register_filter("unlinkat", lambda process, args: filter_delete(process.full_path(args[1], args[0])))
register_filter("rmdir", lambda process, args: filter_delete(process.full_path(args[0])))
