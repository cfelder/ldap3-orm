# coding: utf-8
"""
This module provides the connection singleton derived from the configuration
and the connection decorator.

In order to use just the :py:decorator:`ldap3_orm.connection.connection`
or the :py:func:`ldap3_orm.connection.create_connection` without creating the
connection singleton please import directly from `_connection`.
"""

from ldap3_orm.config import config
# pylint: disable=unused-import
from ldap3_orm._connection import Connection, connection, create_connection
# pylint: disable=unused-import
# pylint: disable=protected-access
# noinspection PyProtectedMember
from ldap3_orm._version import __version__, __revision__


__author__ = "Christian Felder <webmaster@bsm-felder.de>"
__copyright__ = """Copyright 2018-2025, Christian Felder

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


conn = create_connection(config.url, config.connconfig)
