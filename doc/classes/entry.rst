****************
ldap3-orm module
****************

This module provides classes for creating object-relational mappings for
LDAP data. In particular it provides the base class
:py:class:`~ldap3_orm.entry.EntryBase` which uses class attributes in order to
configure the *ORM model* and dynamically creates a appropriate constructor
with the objective of writing less code and to focus on the configuration.

ORM Modelling
=============

.. module:: ldap3_orm

.. autoclass:: ParamDef
   :members:

.. autoclass:: EntryBase
   :members:

Automatic ORM Model Creation
============================

.. autoclass:: EntryType

.. _entry-orm_filter:

ORM Filter Expressions
======================

ldap3-orm supports querying LDAP directories without any knowledge about the
LDAP filter syntax defined in RFC 4515 simply using ORM models and Python
operators. Nevertheless the usual LDAP filter syntax as well as the Simplified
Query Language defined in the `ldap3 project <http://ldap3.readthedocs.io>`_
and ORM Filter Expressions can be used vice versa.


.. note::

   ldap3-orm filter expressions can be used on :py:class:`ldap3_orm.Connection
   <ldap3.core.connection.Connection>` and :py:class:`ldap3_orm.Reader
   <ldap3.abstract.cursor.Reader>` objects. Please ensure that you are importing
   those classes from the :py:mod:`ldap3_orm` module and not from
   :py:mod:`ldap3`. Both classes inherit from its originating ones and have
   just been extended to support ORM Filter Expressions.


Assuming we have created the following ORM model for a LDAP user entry:

.. literalinclude:: /examples/user.py
   :caption: user.py


and we have created an active :py:class:`ldap3_orm.Connection
<ldap3.core.connection.Connection>` object::

   >>> from ldap3_orm import ALL_ATTRIBUTES, Connection, ObjectDef, Reader
   >>> with Connection("ldap://ldap.example.com", "cn=directory manager",
                       "secret", auto_bind=True) as conn:

We can query for an user entry using his unique username.

   >>> search_base = "ou=People,dc=example,dc=com"
   >>> conn.search(search_base, User.username == "guest",
                   attributes=ALL_ATTRIBUTES)
   True
   >>> conn.entries
   [DN: uid=guest,ou=People,dc=example,dc=com - STATUS: Read - READ TIME:
   2018-03-15T14:32:00.369434
       cn: Guest User
       givenName: Guest
       mail: guest.user@example.com
       sn: User
       uid: guest
       userPassword: {SSHA}oKJYPtoC+8mPBn/f47cSK5xWJuap183E
   ]

We can have a look at the internaly generated LDAP filter.

   >>> User.username == "guest"
   uid - mandatory: False - filter: (uid=jcnsgast)
   >>> print(User.username == "guest")
   '(uid=guest)'

We can use :py:class:`ldap3_orm.Reader <ldap3.abstract.cursor.Reader>` objects.

   >>> r = Reader(conn, ObjectDef("inetOrgPerson", conn), search_base,
                  User.username == "guest")
   >>> r.query_filter
   '(&(objectClass=inetOrgPerson)(uid=guest))'
   >>> r.query
   (uid=guest)
   >>> r.search()
   [DN: uid=guest,ou=People,dc=example,dc=com - STATUS: Read - READ TIME:
   2018-03-15T14:32:00.369434
   >>> r[0]
   DN: uid=guest,ou=People,dc=example,dc=com - STATUS: Read - READ TIME:
   2018-03-15T14:32:00.369434

Instead of creating our own models we can dynamically create a model from
our active connection using either
:py:class:`ldap3_orm.ObjectDef <ldap3.abstract.objectDef.ObjectDef>`

   >>> odef = ObjectDef("inetUser", conn)
   >>> odef
   OBJ : inetUser
   AUX : <None>
   OID: inetUser (Auxiliary) 2.16.840.1.113730.3.2.130, top (Abstract) 2.5.6.0
   MUST: objectClass
   MAY : inetUserHttpURL, inetUserStatus, memberOf, uid, userPassword
   >>> print(odef.uid == "guest")
   '(uid=guest)'

or a class generated from the :py:class:`~ldap3_orm.entry.EntryType` factory.

   >>> InetUser = EntryType("uid={uid},ou=People," + config.base_dn,
                            "inetUser", conn)
   >>> print(InetUser.uid == "guest")
   '(uid=guest)'

Operators
---------

The following examples show some of ldap3-orm's ORM Filter Expression
capabilities. We have already seen that we can equate attributes::

   >>> print(User.username == "guest")
   '(uid=guest)'

ORM Filter Expressions are escaped::

   >>> print(User.givenname == "Gu*")
   (givenName=Gu\2a)

In order to get all users with its givenname starting with ``Gu`` use the
``startswith`` operator::

   >>> print(User.givenname.startswith("Gu"))
   (givenName=Gu*)

For checking endings use the following::

   >>> print(User.givenname.endswith("st"))
   (givenName=*st)

Expressions can be combined using and ``&``, or ``|`` operators::

   >>> print(User.givenname.startswith("Chris")
   ...       & ((User.surname == "Schmitz") | (User.surname == "Maier")))
   (&(givenName=Chris*)(|(sn=Schmitz)(sn=Maier)))
