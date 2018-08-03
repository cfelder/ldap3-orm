#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function

import sys
from os import getenv, path
import argparse
import textwrap
from IPython.terminal.embed import InteractiveShellEmbed
try:
    from ipykernel.ipkernel import IPythonKernel
    from ipykernel.kernelapp import IPKernelApp
except ImportError:
    IPythonKernel = None
    IPKernelApp = None
from ldap3 import Connection
import ldap3_orm.connection
from ldap3_orm.pycompat import callable, iteritems, file_types
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


class ConfigurationError(Exception):
    """Configuration parameter is not allowed."""


def _exec(path_or_file, globals=None, locals=None):
    ns = locals or {}
    if isinstance(path_or_file, file_types):
        fileobj = path_or_file
    else:
        fileobj = argparse.FileType('r')(path_or_file)
    try:
        exec(compile(fileobj.read(), fileobj.name, "exec"), globals, ns)
    finally:
        fileobj.close()
    return ns


def load_config(configfile):
    return _exec(configfile)


def _create_parsers():
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("-c", "--config", type=argparse.FileType('r'),
                        help="configuration file with command line arguments")
    parser = argparse.ArgumentParser(
        description="ldap3-orm ipython shell",
        epilog=textwrap.dedent('''\
        Configuration file:

        The configuration file can provide and/or overwrite any command line
        arguments in its long form except the config and help argument as
        parameters in the form key = value, e.g.

            url = "ldaps://example.com"
            base_dn = "dc=example,dc=com"
            username = "cn=Directory Manager"
            password = "secret"

            modules = [
                "/path/to/module/containing/EntryBase/subclasses",
            ]

            pythonpaths = [
                "/path/to/modules/needed/by/modules/listed/above",
            ]
        '''),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parent],
    )
    parser.add_argument("--url",
                        help="ldap server url in the scheme://hostname:port")
    parser.add_argument("--username",
                        help="the account of the user to log in for simple "
                             "bind"),
    parser.add_argument("--password",
                        help="the password of the user for simple bind")
    parser.add_argument("--base_dn",
                        help="ldap base dn")
    parser.add_argument("-f", help="jupyter kernel connection file (.json)")
    parser.add_argument("-p", "--pythonpaths", nargs='*',
                        help="paths prepended in PYTHONPATH environment")
    parser.add_argument("-m", "--modules", nargs='*',
                        help="python modules to include into current namespace")
    return parent, parser


def create_parser():
    return _create_parsers()[1]


def parse_args(argv):
    argv = argv[:]
    parent, parser = _create_parsers()
    # run parent parser to gather cliargs from the configuration file
    ns = parent.parse_known_args(argv[1:])[0]
    configdir = path.join(getenv("APPDATA",
                                 path.expanduser(path.join("~", ".config"))),
                          "ldap3-ipython")
    configfile = path.join(configdir, "default")
    if not ns.config and path.isfile(configfile):
        ns.config = configfile
    if ns.config:
        config = load_config(ns.config)
        if "config" in config or "help" in config:
            raise ConfigurationError("Configuration parameters 'config' and/or "
                                     "'help' are not allowed in the "
                                     "configuration file '%s'."
                                     % ns.config.name)
        for k, v in iteritems(config):
            argv.append("--" + k)
            if isinstance(v, list):
                argv += v
            else:
                argv.append(v)
    ns = parser.parse_args(argv[1:])
    return ns


def main(argv):
    ns_args = parse_args(argv)
    if ns_args.url and ns_args.username and ns_args.password:
        ldap3_orm.connection.conn = Connection(ns_args.url, ns_args.username,
                                               ns_args.password, auto_bind=True)
        # add conn to locals() in order to populate the new namespace
        conn = ldap3_orm.connection.conn
        if ns_args.base_dn:
            ldap3_orm.connection.base_dn = ns_args.base_dn
            # pylint: disable=unused-import
            from ldap3_orm.basic import search
        # add basic convenience functions to local namespace
        # pylint: disable=unused-import
        from ldap3_orm.basic import add, delete
    else:
        print("Connection object 'conn' has not been created.", file=sys.stderr)
        print("- Insufficient connection parameters -", file=sys.stderr)
    # update local namespace `ns` with cli arguments
    ns = dict(locals())
    modules = ns_args.__dict__.pop("modules", []) or []
    pythonpaths = ns_args.__dict__.pop("pythonpaths", []) or []
    kernelconn = ns_args.__dict__.pop('f', None)
    ns.update(ns_args.__dict__)
    del ns["ns_args"]  # remove temporary namespace variable
    docs = [name + '\t-> ' + cls_or_func.__doc__.split('\n')[0]
            for name, cls_or_func in iteritems(locals())
            if callable(cls_or_func) and cls_or_func.__doc__]

    # prepend pythonpaths to sys.path (PYTHONPATH)
    sys.path = pythonpaths + sys.path
    # execute modules given on the command line in current namespace
    for p in modules:
        _exec(p, ns, ns)

    banner1 = "ldap3-orm interactive shell ({version}, {revision})".format(
        version=__version__, revision=__revision__)
    banner2 = textwrap.dedent("""\
        The following convenience functions are available:

        {functions}

        The current Connection can be accessed using 'conn'.
        """).format(functions='\n'.join(docs)) if docs else ' '


    if kernelconn:  # jupyter kernel connection file
        if IPythonKernel and IPKernelApp:
            class Ldap3IPythonKernel(IPythonKernel):
                implementation = "ldap3-ipython"
                implementation_version = __version__
                banner = banner1 + '\n\n' + banner2

            IPKernelApp.launch_instance(kernel_class=Ldap3IPythonKernel,
                                        user_ns=ns)
        else:
            raise ImportError("No module named ipykernel")
    else:
        InteractiveShellEmbed(banner1=banner1, user_ns=ns)(banner2)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
