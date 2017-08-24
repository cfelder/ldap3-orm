User model example
------------------

The following code creates a simple ORM model for a LDAP user entry::

   from ldap3_orm import EntryBase, AttrDef


   class User(EntryBase):
       dn = "uid={uid},{base_dn}"
       base_dn = "ou=People,dc=example,dc=com"
       object_classes = ["top", "inetUser", "inetOrgPerson"]

       username = AttrDef("uid")
       password = AttrDef("userPassword")
       fullname = AttrDef("cn")
       givenname = AttrDef("givenName")
       surname = AttrDef("sn")
       email = AttrDef("mail")

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
