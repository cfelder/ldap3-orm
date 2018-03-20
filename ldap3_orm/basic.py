# coding: utf-8

from ldap3_orm.connection import connection, conn, base_dn
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


@connection(conn)
def add(conn, entry):
    """Adds a new ``entry`` to the connected LDAP.

    The ``entry`` is passed to the active
    :py:class:`ldap3.Connection <ldap3.core.connection.Connection>`
    ``conn`` in order to create a new LDAP entry.

    """
    return conn.add(entry.entry_dn, entry.object_classes,
                    entry.entry_attributes_as_dict)


@connection(conn)
def delete(conn, entry):
    """Deletes an ``entry`` from the connected LDAP.

    The ``entry`` is passed to the active
    :py:class:`ldap3.Connection <ldap3.core.connection.Connection>`
    ``conn`` in order to delete an existing LDAP entry with the
    specified ``DN``.

    """
    return conn.delete(entry.entry_dn)


@connection(conn, base_dn)
def search(conn, *args, **kwargs):
    """Search the connected LDAP.

    Searches in the connected LDAP using the active
    :py:class:`ldap3.Connection <ldap3.core.connection.Connection>`
    ``conn`` and the configured ``base_dn`` for ``search_base``.
    Further arguments are passed to
    :py:func:`ldap3.Connection.search
    <ldap3.core.connection.Connection.search>` function.

    See ``help(ldap3.Connection.search)`` for more details.

    """
    return conn.search(*args, **kwargs)
