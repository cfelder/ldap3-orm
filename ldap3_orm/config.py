# coding: utf-8
"""
This module provides the configuration singleton
:py:class:`~ldap3_orm._config.config` which is populated on startup of
``ldap3-ipython`` with entries from command line arguments and entries from
the configuration file.

Internal ldap3_orm modules should not use this module and import directly
from `_config` instead. Otherwise ``ldap3-ipython`` cannot apply
configuration options to the :py:class:`~ldap3_orm._config.config` singleton
because ``config.apply()`` will load the default configuration file if
available and start with an unconfigured :py:class:`~ldap3_orm._config.config`
otherwise.
"""

from ldap3_orm._config import config
# pylint: disable=unused-import
# pylint: disable=protected-access
# noinspection PyProtectedMember
from ldap3_orm._version import __version__, __revision__


__author__ = "Christian Felder <webmaster@bsm-felder.de>"
__copyright__ = """Copyright 2018-2020, Christian Felder

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

config.apply()
