# coding: utf-8

from ldap3 import AttrDef as _AttrDef
from ldap3 import ObjectDef as _ObjectDef
from ldap3_orm.attribute import OperatorAttrDef
# pylint: disable=unused-import
# pylint: disable=protected-access
# noinspection PyProtectedMember
from ldap3_orm._version import __version__, __revision__


__author__ = "Christian Felder <webmaster@bsm-felder.de>"
__copyright__ = """Copyright 2016-2018, Christian Felder

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


class ObjectDef(_ObjectDef):

    def __getattr__(self, item):
        attr = _ObjectDef.__getattr__(self, item)
        # intentionally use ldap3 AttrDef on type checking here
        if isinstance(attr, _AttrDef):
            return OperatorAttrDef.create_from_AttrDef(attr)
        return attr
