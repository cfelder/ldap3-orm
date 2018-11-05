# coding: utf-8

from os import getenv, path

from ldap3_orm.pycompat import iteritems
from ldap3_orm.utils import execute
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


CONFIGDIR = path.join(getenv("APPDATA",
                              path.expanduser(path.join("~", ".config"))),
                       "ldap3-ipython")
CONFIGFILE = path.join(CONFIGDIR, "default")


class ConfigurationError(Exception):
    """Configuration parameter is not allowed."""


class FallbackFileType(object):
    """Factory for creating file object types with fallback directory

    Returns a file object using the builtin :py:func:`open`() function.

    If the path passed to an instance of this class does not exist and
    the path contains just a filename (no directories) this class tries
    to open the file in the fallback directory.

    """

    def __init__(self, mode='r', fallback=CONFIGDIR, **kwargs):
        self._mode = mode
        self._kwargs = kwargs
        self._fallback = fallback

    def __call__(self, path_or_filename):
        try:
            return open(path_or_filename, self._mode, **self._kwargs)
        except IOError:
            # argument is just a filename (no directory components)
            if path.basename(path_or_filename) == path_or_filename:
                return open(path.join(self._fallback, path_or_filename),
                            **self._kwargs)
            raise


class config(object):
    """Holds all configuration parameters

    This is a configuration singleton populated on startup of ``ldap3-ipython``
    with entries given as command line arguments and/or entries from the
    configuration file.

    This class is helpful for creating reusable modules based on
    configuration parameters, e.g. ``base_dn`` which usually changes
    when administrating different domains, e.g. ``example.com`` vs.
    ``example.org`` which results in the following ``base_dn`` settings::

        base_dn = "dc=example,dc=com"
        base_dn = "dc=example,dc=org"

    If this class is imported from the :py:mod:`ldap3_orm.config` module
    before any configuration has been applied this class will be populated
    from the default configuration file if this exists or left unpopulated
    otherwise.

    """
    _applied = False  # apply only once

    # -- cli and configuration file arguments ----------------------------
    url = None
    """Ldap server url in the scheme://hostname:port"""

    base_dn = ''
    """Ldap base dn"""

    username = None
    """The account of the user to log in for simple bind"""

    password = None
    """The password of the user for simple bind"""

    modules = None
    """Python modules to include into current namespace in ``ldap3-ipython``"""

    pythonpaths = None
    """Paths prepended in PYTHONPATH environment in ``ldap3-ipython``"""

    # -- arguments only supported in the configuration file --------------
    userconfig = {}
    """Dictionary containing user-defined configuration entries."""

    connconfig = {}
    """Dictionary containing keyword arguments for
    :py:class:`ldap3_orm.Connection <ldap3.core.connection.Connection>`."""

    @classmethod
    def apply(cls, config=None):
        if cls._applied:
            return

        if config is None and path.isfile(CONFIGFILE):
            config = read_config()

        for attr, value in iteritems(config):
            if not hasattr(cls, attr):
                raise ConfigurationError("Configuration parameter '%s' is not "
                                         "allowed in the configuration file."
                                         % attr)
            getattr(cls, attr)  # raises attribute error if attr not exists
            setattr(cls, attr, value)

        cls._applied = True


def read_config(path=CONFIGFILE, cls=FallbackFileType('r')):
    return execute(path, cls=cls)
