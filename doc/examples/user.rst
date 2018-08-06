User model example
------------------

The following code creates a simple ORM model for a LDAP user entry:

.. literalinclude:: /examples/user.py

A User object can be instantiated using *keyword arguments* for each class
attribute of type :py:class:`~ldap3.abstract.attrDef.AttrDef`::

   >>> u = User(username="guest",
                password="{SSHA}oKJYPtoC+8mPBn/f47cSK5xWJuap183E",
                fullname="Guest User",
                givenname="Guest",
                surname="User",
                email="guest.user@example.com")
   >>> u
   DN: uid=guest,ou=People,dc=example,dc=com
       cn: Guest User
       givenName: Guest
       mail: guest.user@example.com
       sn: User
       uid: guest
       userPassword: {SSHA}oKJYPtoC+8mPBn/f47cSK5xWJuap183E

We can pass this object to an active
:py:class:`ldap3.Connection <ldap3.core.connection.Connection>`
in order to create a new LDAP user entry::

   >>> from ldap3 import Connection
   >>> with Connection("ldap://ldap.example.com", "cn=directory manager",
                       "secret", auto_bind=True) as conn:
           conn.add(u.entry_dn, u.object_classes,
                    u.entry_get_attributes_dict)

Assuming the ORM model mentioned above has been stored in a file ``user.py`` an
interactive ldap3-orm shell can be used to create further LDAP user entries
using the following command::

   $ ldap3-ipython -m user.py

.. code-block:: ipython

   ldap3-orm interactive shell (|version|, gcf02018)

   The following convenience functions are available:

   search  -> Search the connected LDAP.
   add     -> Adds a new ``entry`` to the connected LDAP.
   delete  -> Deletes an ``entry`` from the connected LDAP.

   The current Connection can be accessed using 'conn'.


   In [1]: u = User(username="guest",
      ...:          password="{SSHA}oKJYPtoC+8mPBn/f47cSK5xWJuap183E",
      ...:          fullname="Guest User",
      ...:          givenname="Guest",
      ...:          surname="User",
      ...:          email="guest.user@example.com")

   In [2]: add(u)
   Out[2]: True

The same code can be used in `Jupyter <http://jupyter.org>`_ when using the
integrated :ref:`ldap3-ipython kernel <ipython_jupyter_kernel>` which provides
the same functionality as the ldap3-orm shell mentioned above.
