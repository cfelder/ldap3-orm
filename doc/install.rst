Install ldap3-orm
=================

Download
--------

The ldap3-orm package can be downloaded at
https://pypi.python.org/pypi/ldap3-orm.

Install from PyPI
-----------------

ldap-orm can be installed from the Python Package Index using ``pip`` ::

   $ pip install ldap3-orm

``pip`` will cope with package dependencies. Thus there is no need to install
requirements on your own as described below for source code installations.

Git repository and code review
------------------------------

ldap3-orm is maintained in a git repository hosted at
`code.bsm-felder.de <https://code.bsm-felder.de>`_.
In order to checkout a working copy anonymously use the following command. ::

  git clone -c http.sslverify=false \
    https://code.bsm-felder.de/review/bsm-felder/ldap/ldap3-orm

You will find all sources in the directory ``ldap3-orm`` poiting to the current
*master branch* which reflects the current *in develeopment* version.

To refer to a specific release you should checkout a tagged version, e.g. ::

   $ cd ldap3-orm
   $ git tag
   v0.1.0

   $ git checkout v0.1.0 -b release-v0.1.0

Install requirements using pip
------------------------------

You can install the requirements using ``pip``, especially into
your *virtual environment* ::

  $ pip install -r requirements.txt

Depending on your setup you need to install further requirements listed below.

============================= =================================================
File                          Required for
============================= =================================================
``requirements-doc.txt``      Building the Documentation
``requirements-tests.txt``    Running the test suite
============================= =================================================

Install ldap3-orm from sources
------------------------------

If all requirements have been fullfilled you can install ldap3-orm using the
standard distutils/setuptools mechanism. Just run the following command in
the project's root folder. ::

  $ python setup.py install
