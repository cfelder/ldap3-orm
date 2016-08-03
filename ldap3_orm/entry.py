# coding: utf-8

from ldap3 import Attribute, AttrDef
from ldap3 import SEQUENCE_TYPES
from ldap3 import Entry as _Entry
from ldap3.utils.dn import safe_dn
from six import add_metaclass
# pylint: disable=unused-import
from ldap3_orm._version import __version__, __revision__


__author__ = "Christian Felder <webmaster@bsm-felder.de>"
__copyright__ = """Copyright 2016, Christian Felder

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


class EntryMeta(type):

    def __init__(cls, name, bases, attrs):
        type.__init__(cls, name, bases, attrs)
        if not hasattr(cls, "_attrdefs"):
            cls._attrdefs = {}
        # for class inheritance first merge and/or update
        # all _attrdefs in correct order
        newattrdefs = {}
        for base in reversed(bases):
           if hasattr(base, "_attrdefs"):
               newattrdefs.update(base._attrdefs)
        # merge and/or update _attrdefs for current class
        for k, attr in attrs.iteritems():
            if isinstance(attr, AttrDef):
                newattrdefs[k] = attr
                delattr(cls, k)
        cls._attrdefs = newattrdefs


@add_metaclass(EntryMeta)
class EntryBase(_Entry):
    """Base class for creating object-relational mapping ldap entries.

    *Configuring ORM models*

    A mapping can be configured using class attributes of type
    :py:class:`~ldap3.abstract.attrDef.AttrDef`, e.g.::

        class User(EntryBase):
            ...
            username = AttrDef("uid")

    The class attribute ``username`` describes the ldap Attribute ``uid``.
    For each class attribute of type :py:class:`~ldap3.abstract.attrDef.AttrDef`
    a corresponding *keyword argument* in the constructor will be generated
    to initialize this attribute. Thus the ``User`` has one ldap Attribute
    named ``uid`` which has to be set in the constructor e.g. using
    ``username="guest"``. Ldap Attributes can be accessed either by sequence,
    by assignment or as dictionary keys. Keys are not case sensitive.

    Furthermore all class attributes of type
    :py:class:`~ldap3.abstract.attrDef.AttrDef` will be destroyed after
    creating the corresponding ldap Attribute in order to avoid naming
    conflicts, e.g. when the class attribute has the same name as the ldap
    Attribute definition in :py:class:`~ldap3.abstract.attrDef.AttrDef`.
    Thus accessing ``User.username`` will raise
    :py:exc:`~exceptions.AttributeError`.

    For more information about ldap Attribute access, inherited methods, etc.
    have a look at :py:class:`~ldap3.abstract.entry.Entry`.

    *Attributes*

    .. attribute:: dn

    distinguished name, an unique identifier in your ldap tree

    Each subclass of this class must define this attribute.

    This attribute can be defined as a template using python's built-in
    :py:func:`format` function. All class attributes and attributes configured
    via :py:class:`~ldap3.abstract.attrDef.AttrDef` will be expanded.
    Furthermore the generated DN will be normalized and escaped using
    :py:func:`ldap3.utils.dn.safe_dn` function.


    *Example*::

        class User(EntryBase):
            dn = "cn={uid},{base_dn}"
            base_dn = "ou=People,dc=example,dc=com"
            username = AttrDef("uid")

        >>> User(username="guest")
        DN: cn=guest,ou=People,dc=example,dc=com
            uid: guest

    The distinguished name ``DN`` in this example has been initialized with
    the values of the configured ``uid`` ldap attribute and the class attribute
    ``base_dn``.

    """

    # distinguished name template for this class
    dn = None

    def __init__(self, **kwargs):
        if self.dn is None:
            raise NotImplementedError("%s must set the 'dn' attribute"
                                      % self.__class__)
        self.__dict__["_attributes"] = {}
        # initialize attributes from kwargs
        attrdefs = dict(self._attrdefs)
        for k, v in kwargs.iteritems():
            if k in self._attrdefs:
                attrdef = attrdefs.pop(k)
                self._create_attribute(attrdef, v)
            else:
                raise TypeError("__init__() got an unexpected keyword argument"
                                " '%s'" % k)
        # check remaining attributes
        for key in attrdefs.keys():
            if attrdefs[key].default != NotImplemented:
                attrdef = attrdefs.pop(key)
                self._create_attribute(attrdef, attrdef.default)
        # all remaining attributes have no reasonable default value
        # (NotImplemented) and should have been set earlier
        if attrdefs:
             s = " '" if len(attrdefs) == 1 else "s '"
             raise TypeError("__init__() missing the following keyword "
                             "argument" + s + ", ".join(attrdefs.keys()) + "'")

        # self._attributes will be overwritten by _Entry.__init__
        # thus store a copy self._attributes
        attributes = dict(self._attributes)
        fmtdict = dict(self.__class__.__dict__)
        fmtdict.update(attributes)
        _Entry.__init__(self, safe_dn(self.dn.format(**fmtdict)), None)
        # restore self._attributes
        self.__dict__["_attributes"] = attributes

    def _create_attribute(self, attrdef, value):
        tolist = lambda itm: itm if isinstance(itm, SEQUENCE_TYPES) \
                                 else [itm]
        attribute = Attribute(attrdef, self)
        # TODO: check for validator and validate
        attribute.__dict__["values"] = tolist(value)
        self.__dict__["_attributes"][attribute.key] = attribute
