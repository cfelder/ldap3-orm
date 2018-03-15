*************
ldap3-ipython
*************

.. argparse::
   :module: ldap3_orm.main
   :func: create_parser
   :prog: ldap3-ipython
   :noepilog:

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
:py:class:`ldap3.Connection <ldap3.core.connection.Connection>` which can be
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

.. literalinclude:: examples/user.py
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

   In [3]: search("(uid=guest)")
   Out[3]: True

   In [4]: conn.entries
   Out[4]: [DN: uid=guest,ou=People,dc=example,dc=com - STATUS: Read - READ
            TIME: 2018-03-15T14:32:00.369434]

Use further attributes on searches:

.. code-block:: ipython

   In [5]: from ldap3 import ALL_ATTRIBUTES

   In [6]: search('(uid=felder)', attributes=ALL_ATTRIBUTES)
   Out[6]: True

   In [7]: conn.entries
   Out[7]:
   [DN: uid=felder,ou=People,dc=example,dc=com - STATUS: Read - READ
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

   In [8]: delete(u)
   Out[8]: True

or use any functionality provided in ``ipython`` or on the
:py:class:`ldap3.Connection <ldap3.core.connection.Connection>` object ``conn``:

.. code-block:: ipython

   In [9]: ?add
   Signature: add(entry)
   Docstring:
   Adds a new ``entry`` to the connected LDAP.

   The ``entry`` is passed to the active
   :py:class:`ldap3.Connection <ldap3.core.connection.Connection>`
   ``conn`` in order to create a new LDAP entry.
   File:      /.../ldap3-orm/ldap3_orm/main.py
   Type:      function

   In [10]: conn.search(base_dn, '(uid=guest)')
   Out[10]: True

   In [11]: conn.entries
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

