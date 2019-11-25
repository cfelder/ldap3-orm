#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function

import sys
from os import path
from getpass import getpass
import argparse
import textwrap
from IPython.terminal.embed import InteractiveShellEmbed
try:
    from ipykernel.ipkernel import IPythonKernel
    from ipykernel.kernelapp import IPKernelApp
except ImportError:
    IPythonKernel = None
    IPKernelApp = None
from ldap3 import SIMPLE
from ldap3.core.exceptions import LDAPBindError
from ldap3.core.results import RESULT_INVALID_CREDENTIALS, RESULT_CODES
from ldap3_orm._config import CONFIGDIR, ConfigurationError, \
    FallbackFileType, config, read_config
from ldap3_orm.utils import execute
from ldap3_orm.pycompat import callable, input, iteritems, reraise
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


ignored_args_in_config = ['f', "config"]


class ArgparseFallbackFileType(argparse.FileType, FallbackFileType):

    def __init__(self, *args, **kwargs):
        FallbackFileType.__init__(self, *args, **kwargs)
        argparse.FileType.__init__(self, *args, **kwargs)

    def __call__(self, path_or_filename):
        try:
            return argparse.FileType.__call__(self, path_or_filename)
        except argparse.ArgumentTypeError:
            exc_info = sys.exc_info()
            try:
                return FallbackFileType.__call__(self, path_or_filename)
            except IOError:
                reraise(*exc_info)


def load_config(configfile):
    return read_config(configfile, cls=argparse.FileType('r'))


def _create_parsers():
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("-c", "--config", type=ArgparseFallbackFileType('r'),
                        help="configuration file (name or full qualified path)")
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
    # all arguments defined in its long form here should have a corresponding
    # class attribute in `ldap3_orm._config.config`.
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
    # gather cliargs from cmdline for username and password overwrite
    ns_cli = parser.parse_known_args(argv[1:])[0]
    configfile = path.join(CONFIGDIR, "default")
    if not ns.config and path.isfile(configfile):
        ns.config = configfile
    if ns.config:
        cfg = load_config(ns.config)
        if "config" in cfg or "help" in cfg:
            raise ConfigurationError("Configuration parameters 'config' and/or "
                                     "'help' are not allowed in the "
                                     "configuration file '%s'."
                                     % ns.config)
        # generate kwargs from configuration file
        # for arguments known by the parser
        for k, v in iteritems(cfg):
            kwarg = "--" + k
            if kwarg in parser._option_string_actions:
                argv.append(kwarg)
                if isinstance(v, list):
                    argv += v
                else:
                    argv.append(v)
    else:
        cfg = {}
    # parse arguments passed to function and from configuration file
    ns = parser.parse_args(argv[1:])
    fullcfg = dict(ns.__dict__)
    # handle overwrite of username and password arguments
    password = None
    if ns_cli.username:
        if ns_cli.password is not None:
            password = ns_cli.password
        else:
            password = getpass("Password for '%s':" % ns_cli.username)
        if "connconfig" not in cfg:
            cfg["connconfig"] = {}
        # update connconfig['password'] later using `config.set_password`
        cfg["connconfig"].update(user=ns_cli.username)
        # remove overwritten config
        for k in ["username", "password"]:
            fullcfg.pop(k, None)
            cfg.pop(k, None)
    # update configuration with arguments from parser
    cfg.update(fullcfg)
    for key in ignored_args_in_config:
        cfg.pop(key, None)
    # pass configuration to `ldap3_orm.config.config` object
    # this will raise an `ConfigurationError` on unknown arguments
    config.apply(cfg)
    # update password
    if password is None and "password" in config.connconfig and \
            config.connconfig["password"] is None:
        password = getpass("Password for '%s':" % config.connconfig["user"])
    if password is not None:
        config.set_password(password)
    return ns


def main(argv):
    ns_args = parse_args(argv)
    if ns_args.url:
        username = config.connconfig.get("user")
        authentication = config.connconfig.get("authentication")
        if (username and not authentication) or authentication == SIMPLE:
            if username is None:
                username = input("User DN: ")
            if "password" not in config.connconfig:
                config.connconfig.update(user=username)
                config.set_password(getpass("Password for '%s': " % username))
        # add conn to locals() in order to populate the new namespace
        # pylint: disable=unused-import
        for i in range(2):  # max 2 retries on invalidCredentials
            try:
                from ldap3_orm.connection import conn
            except LDAPBindError as e:
                if RESULT_CODES[RESULT_INVALID_CREDENTIALS] not in str(e):
                    break
                print("Invalid credentials.", file=sys.stderr)
                config.set_password(getpass("Password for '%s': " % username))
            else:
                break
        if config.base_dn:
            # pylint: disable=unused-import
            from ldap3_orm.basic import search
        # add basic convenience functions to local namespace
        # pylint: disable=unused-import
        from ldap3_orm.basic import add, delete
    else:
        print("Connection object 'conn' has not been created.", file=sys.stderr)
        print("- Insufficient connection parameters -", file=sys.stderr)
    # update local namespace `ns` with cli arguments and include all `locals()`
    ns = dict(locals())
    modules = config.modules or []
    pythonpaths = config.pythonpaths or []
    kernelconn = ns_args.__dict__.pop('f', None)
    # do not include the following cli args in local namespace `ns`
    del ns_args.__dict__["modules"]
    del ns_args.__dict__["pythonpaths"]
    ns.update(ns_args.__dict__)
    del ns["ns_args"]  # remove temporary namespace variable
    docs = [name + '\t-> ' + cls_or_func.__doc__.split('\n')[0]
            for name, cls_or_func in iteritems(locals())
            if callable(cls_or_func) and cls_or_func.__doc__]

    # prepend pythonpaths to sys.path (PYTHONPATH)
    sys.path = pythonpaths + sys.path
    # execute modules given on the command line in current namespace
    for p in modules:
        execute(p, ns, ns)

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
