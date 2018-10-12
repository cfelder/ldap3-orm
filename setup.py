#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import os.path
import json
from distutils import log
from setuptools import Command
from setuptools import find_packages, setup
from setuptools.command.install import install as _install
try:
    from jupyter_client.kernelspec import install_kernel_spec
except ImportError as err:
    import traceback
    install_kernel_spec = None
    exc_info_install_kernel_spec = sys.exc_info()
try:
    from tempfile import TemporaryDirectory
except ImportError:  # not available in python 2.7
    import shutil as _shutil
    from tempfile import mkdtemp

    # provide a simplified version of `TemporaryDirectory` for using this
    # ``setup.py`` file with python 2.7. For using `TemporaryDIrectory` in
    # python 2.7 in general please use the `backports.tempfile` module.
    class TemporaryDirectory(object):
        """Create and return a temporary directory.  This has the same
        behavior as mkdtemp but can be used as a context manager.  For
        example:

            with TemporaryDirectory() as tmpdir:
                ...

        Upon exiting the context, the directory and everything contained
        in it are removed.
        """

        def __init__(self, suffix='', prefix="tmp", dir=None):
            self.name = mkdtemp(suffix, prefix, dir)

        def __repr__(self):
            return "<{} {!r}>".format(self.__class__.__name__, self.name)

        def __enter__(self):
            return self.name

        def __exit__(self, exc, value, tb):
            self.cleanup()

        def cleanup(self):
            _shutil.rmtree(self.name)


import vcversioner

__author__ = "Christian Felder <webmaster@bsm-felder.de>"
__version__ = vcversioner.find_version(
    version_module_paths=[os.path.join("ldap3_orm",
                                       "_version.py")]).version
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


kernel_json = {
    "argv": [
        sys.executable, "-m", "ldap3_orm.main", "-f", "{connection_file}"
    ],
    "display_name": "ldap3-ipython",
    "name": "ldap3-ipython",
    "language": "python"
}


with open("README.rst", 'r') as fd:
    long_description = fd.read()


class test(Command):
    description = "run nosetest test suite"

    # List of option tuples: long name, short name (None if no short
    # name), and help string.
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import nose
        import ldap3_orm
        log.info("ldap3-orm version:", ldap3_orm.__version__)
        log.info()
        nose.run(argv=[sys.argv[0], "test.ldap3_orm", "-v"])


class install(_install):

    user_options = _install.user_options + [
        ("no-kernelspec-prefix", None,
         "Do not use '--prefix' for kernelspec installation"),
    ]

    def initialize_options(self):
        _install.initialize_options(self)
        self.no_kernelspec_prefix = None

    def run(self):
        _install.run(self)

        if not install_kernel_spec:
            log.error(
                "Cannot import 'jupyter_client' package. "
                "The 'ldap3-ipython' jupyter kernel will *not* "
                "be installed."
            )
            traceback.print_exception(*exc_info_install_kernel_spec)
            return

        kernelspec_prefix = None
        if not self.no_kernelspec_prefix and self.prefix:
            kernelspec_prefix = os.path.normpath(
                (self.root or '') + self.prefix)

        with TemporaryDirectory() as dirname:
            os.chmod(dirname, 0o755)
            with open(os.path.join(dirname, "kernel.json"), 'w') as fd:
                json.dump(kernel_json, fd, sort_keys=True)
            try:
                log.debug("kernelspec_prefix: %r" % kernelspec_prefix)
                install_kernel_spec(dirname, kernel_json["name"], user=False,
                                    prefix=kernelspec_prefix)
            except OSError:
                if kernelspec_prefix:
                    raise

                log.warn("Could not install 'ldap3-ipython' jupyter kernel in "
                         "a system-wide location. Performing user install.")
                install_kernel_spec(dirname, kernel_json["name"], user=True,
                                    prefix=kernelspec_prefix)


def find_scripts(where="bin"):
    return [os.path.join(where, name) for name in os.listdir(where) if
            os.path.isfile(os.path.join(where, name))]


setup(cmdclass={
        "install": install,
        "test": test,
      },
      name="ldap3-orm",
      version=__version__,
      description="ldap3-orm, object-relational mapping for ldap3",
      long_description=long_description,
      author="Christian Felder",
      author_email="webmaster@bsm-felder.de",
      url="https://github.com/cfelder/ldap3-orm",
      license="LGPL-3.0+",
      scripts=find_scripts(),
      packages=find_packages(exclude=["test", "test.*"]),
      include_package_data=True,
      requires=["ldap3", "six"],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "Intended Audience :: System Administrators",
          "License :: OSI Approved :: GNU General Public License v3 or later "
          "(GPLv3+)",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 3",
          "Topic :: Software Development",
          "Topic :: Software Development :: Libraries",
          "Topic :: System :: Systems Administration",
          "Topic :: System :: Systems Administration :: "
          "Authentication/Directory",
          "Topic :: System :: Systems Administration :: "
          "Authentication/Directory :: LDAP",
      ],
     )
