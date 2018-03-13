#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os.path
from distutils.core import Command
from setuptools import find_packages, setup
import vcversioner

__author__ = "Christian Felder <webmaster@bsm-felder.de>"
__version__ = vcversioner.find_version(
    version_module_paths=[os.path.join("ldap3_orm",
                                       "_version.py")]).version
__copyright__ = """Copyright 2016-2017, Christian Felder

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
        import sys
        import nose
        import ldap3_orm
        print("ldap3-orm version:", ldap3_orm.__version__)
        print()
        nose.run(argv=[sys.argv[0], "test.ldap3_orm", "-v"])


setup(cmdclass={"test": test},
      name="ldap3-orm",
      version=__version__,
      description="ldap3-orm, object-relational mapping for ldap3",
      author="Christian Felder",
      author_email="webmaster@bsm-felder.de.de",
      url="http://code.bsm-felder.de/doc/ldap3-orm",
      license="LGPL-3.0+",
      scripts=[os.path.join("bin", "ldap3-ipython")],
      packages=find_packages(exclude=["test"]),
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
