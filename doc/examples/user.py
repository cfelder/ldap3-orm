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
