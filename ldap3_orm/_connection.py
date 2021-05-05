# coding: utf-8

from functools import partial

from ldap3 import Connection as _Connection
# pylint: disable=unused-import
# pylint: disable=protected-access
# noinspection PyProtectedMember
from ldap3_orm._version import __version__, __revision__
from ldap3_orm.utils import compile_filter

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


class Connection(_Connection):

    def search(self, search_base, search_filter, *args, **kwargs):
        query = compile_filter(search_filter)
        return _Connection.search(self, search_base, query, *args, **kwargs)


def create_connection(url, connconfig, auto_bind=True):
    """Create :py:class:`ldap3_orm.Connection
    <ldap3.core.connection.Connection>` from configuration. The
    ``auto_bind`` flag can either be set as keyword argument or provided in the
    ``connconfig`` dictionary which has preference in case both options are
    used.

    """
    if connconfig:
        if "auto_bind" not in connconfig:
            connconfig = dict(auto_bind=auto_bind, **connconfig)
        return Connection(url, **connconfig)
    return Connection(url, auto_bind=auto_bind)


def connection(conn, *add_args):
    """Passes a :py:class:`ldap3_orm.Connection
    <ldap3.core.connection.Connection>` object to the decorated function as
    first argument and further arguments passed to the decorator.

    """
    def decorator(func):
        if conn == NotImplemented:
            new_func = partial(func, *add_args)
        else:
            new_func = partial(func, conn, *add_args)
        new_func.__doc__ = func.__doc__
        return new_func
    return decorator
