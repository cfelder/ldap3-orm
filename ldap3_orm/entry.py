# coding: utf-8

from ldap3 import Attribute, AttrDef
from ldap3 import SEQUENCE_TYPES
from ldap3 import Entry as _Entry
from ldap3.abstract import STATUS_WRITABLE as _STATUS_WRITEABLE
from ldap3.abstract.entry import EntryState as _EntryState
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
        # all _attrdefs and object_classes in correct order
        newattrdefs = {}
        newobjclss = set()
        for base in reversed(bases):
            if hasattr(base, "_attrdefs"):
                newattrdefs.update(base._attrdefs)
            if hasattr(base, "object_classes"):
                newobjclss.update(set(base.object_classes))
        # merge and/or update _attrdefs for current class
        for k, attr in attrs.iteritems():
            if isinstance(attr, AttrDef):
                newattrdefs[k] = attr
                delattr(cls, k)
        cls._attrdefs = newattrdefs
        # update object_classes for current class
        newobjclss.update(set(cls.object_classes))
        cls.object_classes = newobjclss


@add_metaclass(EntryMeta)
class EntryBase(_Entry):
    """Base class for creating object-relational mapping ldap entries.

    *Configuring ORM models*

    A mapping can be configured using class attributes of type
    :py:class:`~ldap3.abstract.attrDef.AttrDef`, e.g.::

        class User(EntryBase):
            ...
            username = AttrDef("uid")

    The class attribute ``username`` describes the ldap attribute ``uid``.
    For each class attribute of type :py:class:`~ldap3.abstract.attrDef.AttrDef`
    a corresponding *keyword argument* in the constructor will be generated
    to initialize this attribute. Thus the ``User`` has one ldap attribute
    named ``uid`` which has to be set in the constructor e.g. using
    ``username="guest"``. Ldap attributes can be accessed either by sequence,
    by assignment or as dictionary keys. Keys are not case sensitive.

    Furthermore all class attributes of type
    :py:class:`~ldap3.abstract.attrDef.AttrDef` will be destroyed after
    creating the corresponding ldap attribute in order to avoid naming
    conflicts, e.g. when the class attribute has the same name as the ldap
    attribute definition in :py:class:`~ldap3.abstract.attrDef.AttrDef`.
    Thus accessing ``User.username`` will raise
    :py:exc:`~exceptions.AttributeError`.

    For more information about ldap attribute access, inherited methods, etc.
    have a look at :py:class:`~ldap3.abstract.entry.Entry`.

    Validation of ldap attributes can be configured by passing
    validate = *callable* to :py:class:`~ldap3.abstract.attrDef.AttrDef`
    where *callable* must accept two arguments, the attribute key and the
    value which should be assigned to the attribute. The *callable* must
    return a boolean allowing or denying the validation or raise an exception.

    *Attributes*

    .. attribute:: dn

       distinguished name, an unique identifier in your ldap tree

       Each subclass of this class must define this attribute.

       This attribute can be defined as a template using python's built-in
       :py:func:`format` function. All class attributes and attributes
       configured via :py:class:`~ldap3.abstract.attrDef.AttrDef` will be
       expanded. Furthermore the generated DN will be normalized and escaped
       using the :py:func:`ldap3.utils.dn.safe_dn` function.


    .. attribute:: object_classes

       a set of object classes to which an entry of this class belongs,
       necessary for creating an new entry in the ldap tree.

    *Example*::

        validateuser = lambda _, value: value.isalpha()


        class User(EntryBase):
            dn = "cn={uid},{base_dn}"
            base_dn = "ou=People,dc=example,dc=com"
            username = AttrDef("uid", validate=validateuser)

        >>> User(username="guest")
        DN: cn=guest,ou=People,dc=example,dc=com
            uid: guest

    The distinguished name ``DN`` in this example has been initialized with
    the values of the configured ``uid`` ldap attribute and the class attribute
    ``base_dn``.

    The ``username`` has been validated using ``validateuser`` which accepts
    only alphabetic characters. Thus the following code will raise
    :py:exc:`~exceptions.TypeError`. ::

        >>> User(username="guest42")
        TypeError: Validation failed for attribute 'uid'
                   and value 'guest42'

    """

    # distinguished name template for this class
    dn = None

    # set of ldap object classes for this entry
    object_classes = set()

    def __init__(self, **kwargs):
        class _DummyCursor(object):  # needed for _EntryState
            definition = None

        if self.dn is None:
            raise NotImplementedError("%s must set the 'dn' attribute"
                                      % self.__class__)
        cursor = _DummyCursor()
        self.__dict__["_state"] = _EntryState(None, cursor)
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

        # self._state will be overwritten by _Entry.__init__
        # thus store a copy self._state
        state = self._state
        fmtdict = dict((k, getattr(self.__class__, k))
                       for k in dir(self.__class__))
        fmtdict.update(self._state.attributes)

        safedn = safe_dn(self.dn.format(**fmtdict))
        _Entry.__init__(self, safedn, cursor)
        state.dn = safedn
        state.set_status(_STATUS_WRITEABLE)

        # restore self._state
        self.__dict__["_state"] = state

    def _create_attribute(self, attrdef, value):
        tolist = lambda itm: itm if isinstance(itm, SEQUENCE_TYPES) \
                                 else [itm]
        attribute = Attribute(attrdef, self, None)
        attribute.__dict__["values"] = tolist(value)
        # check for validator
        if attrdef.validate:
            # call validator with attribute key and the corresponding value
            # which should be assigned to the attribute.
            if not attrdef.validate(attribute.key, attribute.value):
                raise TypeError("Validation failed for attribute '%s' "
                                "and value '%s'" % (attribute.key,
                                                    attribute.value))
        self._state.attributes[attribute.key] = attribute
