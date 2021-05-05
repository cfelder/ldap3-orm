# coding: utf-8

from ldap3 import Attribute
from ldap3_orm.attribute import AttrDef
# pylint: disable=unused-import
# pylint: disable=protected-access
# noinspection PyProtectedMember
from ldap3_orm._version import __version__, __revision__


__author__ = "Christian Felder <webmaster@bsm-felder.de>"
__copyright__ = """Copyright 2018-2021, Christian Felder

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


class ParamDef(AttrDef):
    """Hold the definition of a parameter

    This class provides a parameter definition which can be used in addition to
    attributes defined using :py:class:`~ldap3.abstract.attrDef.AttrDef`. The
    parameter definition is used in the same way as for
    :py:class:`~ldap3.abstract.attrDef.AttrDef` except that it is not added
    the schema.

    """


class Parameter(Attribute):
    """Parameter/values object created from :py:class:`~ldap3_orm.ParamDef`."""
