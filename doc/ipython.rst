*************
ldap3-ipython
*************

.. _ipython_argparse:

.. argparse::
   :module: ldap3_orm.main
   :func: create_parser
   :prog: ldap3-ipython
   :noepilog:

.. _ipython_config:

Configuration File
==================

By default ``ldap3-ipython`` searches for the ``default`` configuration file
in ``~/.config/ldap3-ipython`` respectively ``$APPDATA/ldap3-ipython`` if no
different configuration file has been specified on the command line otherwise.

The configuration file can provide and/or overwrite any command line
arguments in its long form except the config and help argument as parameters
in the form key = value, e.g.::

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

The configuration file may provide additional configuration options, e.g. the
``connconfig`` dictionary for using different authentication mechanisms or the
``userconfig`` dictionary which may be used for providing configuration options
for custom module implementations. For further information have a look at
:py:class:`ldap3_orm.config.config`.

The configuration file above is an example for using ldap simple
authentication. Different authentication mechanisms supported in
:py:class:`ldap3_orm.Connection <ldap3.core.connection.Connection>` can be
configured providing the ``url`` entry and all relevant keyword arguments
for its constructor using the ``connconfig`` dictionary, e.g.::

   url = "ldapi:///var/run/slapd/ldapi"
   base_dn = "dc=example,dc=com"

   modules = [
       "/path/to/module/containing/EntryBase/subclasses",
   ]

   pythonpaths = [
      "/path/to/modules/needed/by/modules/listed/above",
   ]

   connconfig = dict(
      authentication = "SASL",
      sasl_mechanism = "GSSAPI",
      sasl_credentials = (True, ),
   )

Usage
=====

The following command will start a new interactive ldap3-orm shell::

   $ ldap3-ipython

If no default configuration file can be found and no further command line
arguments are given this will result in the following offline ldap3-orm
interactive shell:

.. code-block:: ipython

   Connection object 'conn' has not been created.
   - Insufficient connection parameters -
   ldap3-orm interactive shell (|version|, gcf02018)



   In [1]:

Otherwise the shell provides an active
:py:class:`ldap3_orm.Connection <ldap3.core.connection.Connection>` which can be
accessed using ``conn`` and some convenience funtions which internally use the
same connection, see below:

.. code-block:: ipython

   ldap3-orm interactive shell (|version|, gcf02018)

   The following convenience functions are available:

   search  -> Search the connected LDAP.
   add     -> Adds a new ``entry`` to the connected LDAP.
   delete  -> Deletes an ``entry`` from the connected LDAP.

   The current Connection can be accessed using 'conn'.


   In [1]: conn
   Out[1]: Connection(server=Server(host='example.com', port=636, ...))

Assuming we have created the following ORM model for a LDAP user entry:

.. literalinclude:: /examples/user.py
   :caption: user.py

We can load this code into the current namespace of a new ldap3-orm
interactive shell::

   $ ldap3-ipython -m user.py

We can add new LDAP user entries using:

.. code-block:: ipython

   In [1]: u = User(username="guest",
      ...:          password="{SSHA}oKJYPtoC+8mPBn/f47cSK5xWJuap183E",
      ...:          fullname="Guest User",
      ...:          givenname="Guest",
      ...:          surname="User",
      ...:          email="guest.user@example.com")

   In [2]: add(u)
   Out[2]: True

Search for LDAP entries using:

.. code-block:: ipython

   In [3]: search(User.username == "guest")
   Out[3]: True

   In [4]: conn.entries
   Out[4]: [DN: uid=guest,ou=People,dc=example,dc=com - STATUS: Read - READ
            TIME: 2018-03-15T14:32:00.369434]

or using the standard LDAP filter syntax defined in RFC 4515:

.. code-block:: ipython

   In [4]: search("(uid=guest)")
   Out[4]: True

   In [5]: conn.entries
   Out[5]: [DN: uid=guest,ou=People,dc=example,dc=com - STATUS: Read - READ
            TIME: 2018-03-15T14:32:00.369434]

Use further attributes on searches:

.. code-block:: ipython

   In [6]: from ldap3 import ALL_ATTRIBUTES

   In [7]: search(User.username == "guest", attributes=ALL_ATTRIBUTES)
   Out[7]: True

   In [8]: conn.entries
   Out[8]:
   [DN: uid=guest,ou=People,dc=example,dc=com - STATUS: Read - READ
    TIME: 2018-03-15T14:35:57.747751
        cn: Guest User
        givenName: Guest
        mail: guest.user@example.com
        objectClass: top
                     inetuser
                     inetorgperson
        sn: User
        uid: guest
        userPassword: {SSHA}oKJYPtoC+8mPBn/f47cSK5xWJuap183E]

Delete entries from the connected LDAP:

.. code-block:: ipython

   In [9]: delete(u)
   Out[9]: True

or use any functionality provided in ``ipython`` or on the
:py:class:`ldap3_orm.Connection <ldap3.core.connection.Connection>` object ``conn``:

.. code-block:: ipython

   In [10]: ?add
   Signature: add(entry)
   Docstring:
   Adds a new ``entry`` to the connected LDAP.

   The ``entry`` is passed to the active
   :py:class:`ldap3_orm.Connection <ldap3.core.connection.Connection>`
   ``conn`` in order to create a new LDAP entry.
   File:      /.../ldap3-orm/ldap3_orm/main.py
   Type:      function

   In [11]: conn.search(base_dn, '(uid=guest)')
   Out[11]: True

   In [12]: conn.entries
   Out[12]: [DN: uid=guest,ou=People,dc=example,dc=com - STATUS: Read - READ
             TIME: 2018-03-15T14:32:00.369434]

The ``base_dn`` parameter either provided in the configuration file or given on
the command line is included in the current namespace. In order to list all
names available in the current scope use the :py:func:`dir()` function.

.. code-block:: ipython

   In [13]: dir()
   Out[13]:
   ['ALL_ATTRIBUTES',
    'AttrDef',
    'EntryBase',
    'In',
    'Out',
    'User',
    '_',
    ...
    'add',
    'argv',
    'base_dn',
    'config',
    'conn',
    'delete',
    'exit',
    'get_ipython',
    'password',
    'quit',
    'search',
    'url',
    'username']

Extending ldap3-ipython
=======================

In addition to ORM models provided in python modules passed to `ldap3-ipython`
new functions using the active
:py:class:`ldap3_orm.Connection <ldap3.core.connection.Connection>` can be
implemented using the :py:func:`ldap3_orm.connection.connection` decorator.

.. py:decorator:: ldap3_orm.connection.connection
.. autofunction:: ldap3_orm.connection.connection

Assuming we want to search for the next free ``uidNumber`` for a
``posixAccount`` in a given range we can use the following code:

.. code-block:: python
   :caption: userid.py

   from ldap3_orm.config import config
   from ldap3_orm.connection import connection, conn


   uid_range = range(20000, 25000 + 1)  # min, max uid


   @connection(conn, "ou=People," + config.base_dn)
   def nextuid(conn, uid_base_dn):
       conn.search(uid_base_dn, "(objectClass=posixAccount)",
                   attributes="uidNumber")
       ids = sorted(set(uid_range) - set(e.uidNumber.value for e in
                                         conn.entries))
       return ids.pop(0)

Please take into account that the code above has been written as a simple
example and is not optimized in several aspects.

* The function queries the directory for all already registered ``uidNumbers``
  and generates a list of free ``ids`` in a given range but it returns just the
  first item/id in the list.

* The function queries the directory at every call.

* The function returns the same ``uidNumber`` twice if the directory has not
  been changed between both calls.

Nevertheless we can load this function into the current namespace of a new
ldap3-orm interactive shell::

   $ ldap3-ipython -m userid.py

and query for the next free ``uidNumber`` using:

.. code-block:: ipython

   In [1]: nextuid()
   Out[1]: 20000

Let's have a look at the import statement again::

  from ldap3_orm.config import config
  from ldap3_orm.connection import connection, conn

* ``config`` holds the :py:class:`~ldap3_orm.config.config` singleton with all
  parameters given in the :ref:`ipython_config` and/or on the
  :ref:`command line <ipython_argparse>`.
* ``connection`` is the decorator
* ``conn`` holds the active
  :py:class:`ldap3_orm.Connection <ldap3.core.connection.Connection>` created
  during startup of `ldap3-ipython`

Let's have a look at the function signature::

   @connection(conn, "ou=People," + config.base_dn)
   def nextuid(conn, uid_base_dn):

* The active :py:class:`ldap3_orm.Connection <ldap3.core.connection.Connection>`
  will be passed internally to ``nextuid()`` as first argument.
* The search base ``"ou=People," + config.base_dn`` will be passed internally
  to the function as second argument.

.. _ipython_jupyter_kernel:

Jupyter Kernel
==============

ldap3-orm can be used in `Jupyter <http://jupyter.org>`_ either by using the
`IPython kernel <https://ipython.readthedocs.io/en/stable/install/kernel_install.html>`_
or by using the ldap3-ipython kernel. The latter provides already an active
:py:class:`ldap3_orm.Connection <ldap3.core.connection.Connection>` which can
be accessed using ``conn`` and some convenience functions just as well as the
ldap3-orm interactive shell if configured properly without writing a single
line of code.

The ldap3-ipython kernel shares the same :ref:`ipython_config` as
``ldap3-ipython``. As it is not possible to pass arguments to the
jupyter kernel invocation, e.g. when using the
``jupyter notebook`` command, all necessary options should be specified in
the :ref:`ipython_config`. The same set of functionality as if launching
``ldap3-ipython`` without arguments will be accessible in every jupyter
notebook using the ldap3-ipython kernel.
