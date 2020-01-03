# coding: utf-8

import io
from ldap3 import SEQUENCE_TYPES
from ldap3_orm.attribute import OperatorAttrDef
from ldap3_orm.pycompat import file_types
# pylint: disable=unused-import
# pylint: disable=protected-access
# noinspection PyProtectedMember
from ldap3_orm._version import __version__, __revision__


__author__ = "Christian Felder <webmaster@bsm-felder.de>"
__copyright__ = """Copyright 2018, Christian Felder

This file is part of ldap3-orm, object-relational mapping for ldap3.

ldap3-orm is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ldap3-orm is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with ldap3-orm. If not, see <http://www.gnu.org/licenses/>.

"""


def execute(path_or_file, globals=None, locals=None, cls=io.FileIO):
    ns = locals or {}
    if isinstance(path_or_file, file_types):
        fileobj = path_or_file
    else:
        fileobj = cls(path_or_file)
    try:
        exec(compile(fileobj.read(), fileobj.name, "exec"), globals, ns)
    finally:
        fileobj.close()
    return ns


def compile_filter(search_filter):
    """Returns a compiled filter representation for
    :py:class:`~ldap3_orm.attribute.OperatorAttrDef`

    or the unmodified ``search_filter`` otherwise.

    """
    if isinstance(search_filter, OperatorAttrDef):
        return search_filter.compiled_filter()
    return search_filter


def tolist(itm):
    return itm if isinstance(itm, SEQUENCE_TYPES) else [itm]


def fmt_class_name(object_classes):
    """Returns a string representation of ``object_classes`` which can be
    used as a class name."""
    if isinstance(object_classes, SEQUENCE_TYPES):
        object_classes = '_'.join(object_classes)
    return object_classes[0].upper() + object_classes[1:]
