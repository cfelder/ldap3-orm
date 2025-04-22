# coding: utf-8

import textwrap

from ldap3 import Attribute
from ldap3 import Entry as _Entry
from ldap3.abstract import STATUS_WRITABLE as _STATUS_WRITEABLE
from ldap3.abstract.entry import EntryState as _EntryState
from ldap3.core.exceptions import LDAPCursorError
from ldap3.utils.ciDict import CaseInsensitiveWithAliasDict
from ldap3.utils.dn import safe_dn

from ldap3_orm.attribute import AttrDef, OperatorAttrDef
from ldap3_orm.objectDef import ObjectDef
from ldap3_orm.pycompat import add_metaclass, iteritems
from ldap3_orm.parameter import Parameter, ParamDef
from ldap3_orm.utils import fmt_class_name, tolist
# pylint: disable=unused-import
# pylint: disable=protected-access
# noinspection PyProtectedMember
from ldap3_orm._version import __version__, __revision__


__author__ = "Christian Felder <webmaster@bsm-felder.de>"
__copyright__ = """Copyright 2016-2025, Christian Felder

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


class EntryState(_EntryState):

    def __init__(self, *args, **kwargs):
        _EntryState.__init__(self, *args, **kwargs)
        self.parameters = CaseInsensitiveWithAliasDict()

    @property
    def defintion(self):
        return self.cursor.definition

    @defintion.setter
    def definition(self, object_def):
        self.cursor.definition = object_def


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
                # pylint: disable=protected-access
                # noinspection PyProtectedMember
                newattrdefs.update(base._attrdefs)
            if hasattr(base, "object_classes"):
                newobjclss.update(set(base.object_classes))
        # merge and/or update _attrdefs for current class
        for k, attr in iteritems(attrs):
            if isinstance(attr, AttrDef):
                newattrdefs[k] = attr
                delattr(cls, k)
        newattrdefs.update(cls._attrdefs)
        cls._attrdefs = newattrdefs
        # update object_classes for current class
        newobjclss.update(set(cls.object_classes))
        cls.object_classes = newobjclss

    def __getattr__(cls, key):
        if "_attrdefs" in cls.__dict__:
            if key in cls._attrdefs:
                # create OperatorAttrDef instance from AttrDef instance
                return OperatorAttrDef.create_from_AttrDef(cls._attrdefs[key])
        raise AttributeError("\'%s\' has no attribute \'%s\'" % (cls.__name__,
                                                                 key))

    def __dir__(cls):
        if hasattr(type, "__dir__"):  # python 3
            attrs = set(type.__dir__(cls))
        else:  # python 2
            attrs = set()
            for base in cls.__bases__:
                attrs.update(set(base.__dict__.keys()))
        attrs.update(cls._attrdefs.keys())
        return list(attrs)

    def __repr__(cls):
        mandatory = []
        optional = []
        for kwarg in sorted(cls._attrdefs):
            attr = cls._attrdefs[kwarg]
            s = "{} ({})".format(kwarg, attr.name) if kwarg != attr.name else \
                kwarg
            if attr.mandatory:
                mandatory.append(s)
            else:
                optional.append(s)
        return textwrap.dedent("""\
        OBJ : {obj}
        DN  : {dn}
        MUST: {mandatory}
        MAY : {optional}
        """).format(
            obj=", ".join(cls.object_classes) if cls.object_classes else
            "<None>",
            dn=cls.dn,
            mandatory=", ".join(mandatory),
            optional=", ".join(optional),
        )


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

    Ldap attributes are declared mandatory in
    :py:class:`~ldap3.abstract.attrDef.AttrDef` by default. This can be changed
    either providing a reasonable default value using the ``default`` keyword
    argument or setting ``mandatory=False``.

    If the class attribute has the same name as the ldap attribute the latter
    will be resolved when accessing the attribute on an instance whereas the
    class attribute will be resolved when accessed on the class. Furthermore
    all class attributes of type :py:class:`~ldap3.abstract.attrDef.AttrDef`
    will be promoted to :py:class:`~ldap3_orm.attribute.OperatorAttrDef` in
    order to support filter expressions.

    For more information about ldap attribute access, inherited methods, etc.
    have a look at :py:class:`~ldap3.abstract.entry.Entry`.

    For more information about filter expressions have a look at
    :ref:`entry-orm_filter`.

    Validation of ldap attributes can be configured by passing
    validate = *callable* to :py:class:`~ldap3.abstract.attrDef.AttrDef`
    where *callable* must accept the value which should be assigned to the
    attribute as argument. The *callable* must return a boolean allowing or
    denying the validation or raise an exception.

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

        validateuser = lambda value: value.isalpha()


        class User(EntryBase):
            dn = "uid={uid},{base_dn}"
            base_dn = "ou=People,dc=example,dc=com"
            username = AttrDef("uid", validate=validateuser)

        >>> User(username="guest")
        DN: uid=guest,ou=People,dc=example,dc=com
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

    In order to support *keyword arguments* used as a template for the DN
    it is possible to define parameter definitions using
    :py:class:`~ldap3_orm.ParamDef` in the same way as
    :py:class:`~ldap3.abstract.attrDef.AttrDef`, except that they are not added
    as ldap attributes.

    *Example*::

        class Automount(EntryBase):
            dn = "cn={cn},ou={automap},{base_dn}"
            base_dn = "cn=automount,dc=example,dc=com"
            object_classes = ["top", "automount"]
            autofile = ParamDef("automap", default="auto.master")
            key = AttrDef("cn")
            info = AttrDef("automountInformation")

         >>> Automount(key="/Scratch", info="examplenfs.example.com:/Scratch",
                       autofile="auto_nfs")
         DN: cn=/Scratch,ou=auto_nfs,cn=automount,dc=example,dc=com
             automountInformation: examplenfs.example.com:/Scratch
             cn: /Scratch

    """

    # distinguished name template for this class
    dn = None

    # set of ldap object classes for this entry
    object_classes = set()

    def __init__(self, **kwargs):
        class _DummyCursor(object):  # needed for _EntryState
            def __init__(self, object_def):
                self.definition = object_def

        if self.dn is None:
            raise NotImplementedError("%s must set the 'dn' attribute"
                                      % self.__class__)
        cursor = _DummyCursor(ObjectDef(self.object_classes))
        self.__dict__["_state"] = EntryState(None, cursor)
        # initialize attributes from kwargs
        attrdefs = dict(self._attrdefs)
        for k, v in iteritems(kwargs):
            if k in self._attrdefs:
                attrdef = attrdefs.pop(k)
                self._create_attribute_or_parameter(attrdef, v)
            else:
                raise TypeError("__init__() got an unexpected keyword argument"
                                " '%s'" % k)
        # check remaining attributes
        for key in list(attrdefs):
            if attrdefs[key].default != NotImplemented:
                attrdef = attrdefs.pop(key)
                self._create_attribute_or_parameter(attrdef, attrdef.default)
            elif not attrdefs[key].mandatory:
                # delete non mandatory attrdef and add to definition
                self._state.definition += attrdefs.pop(key)
        # all remaining attributes are mandatory, do not provide a reasonable
        # default value (NotImplemented) and should have been set earlier
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
        fmtdict.update(self._state.parameters)

        safedn = safe_dn(self.dn.format(**fmtdict))
        _Entry.__init__(self, safedn, cursor)
        state.dn = safedn
        state.set_status(_STATUS_WRITEABLE)

        # restore self._state
        self.__dict__["_state"] = state

    def _create(self, attrdef, value, cls, state_parameters_or_attributes):
        attribute = cls(attrdef, self, None)
        attribute.__dict__["values"] = tolist(value)
        # check for validator
        if attrdef.validate:
            # call validator with the value which should be assigned to the
            # attribute.
            if not attrdef.validate(attribute.value):
                raise TypeError("Validation failed for attribute '%s' "
                                "and value '%s'" % (attribute.key,
                                                    attribute.value))
        state_parameters_or_attributes[attribute.key] = attribute
        state_parameters_or_attributes.set_alias(attribute.key,
                                                 attrdef.other_names or [])

    def _create_attribute(self, attrdef, value):
        # add Attributes to the schema definition self._state.attributes
        self._create(attrdef, value, Attribute, self._state.attributes)
        # add raw_attributes without processing
        self._state.raw_attributes[attrdef.key] = tolist(value)
        self._state.definition += attrdef

    def _create_parameter(self, attrdef, value):
        # do not add Parameters to the schema
        self._create(attrdef, value, Parameter, self._state.parameters)

    def _create_attribute_or_parameter(self, attrdef, value):
        if isinstance(attrdef, ParamDef):
            self._create_parameter(attrdef, value)
        else:  # AttrDef
            self._create_attribute(attrdef, value)

    def __getattr__(self, item):
        """Return the corresponding class attribute if the attribute on the
        instance does not exist taking into account dynamic class attributes
        provided in :py:class:`~ldap3_orm.entry.EntryMeta`s
        :py:func:`__getattr__` implementation.

        """
        try:
            attr = _Entry.__getattr__(self, item)
        except (AttributeError, LDAPCursorError):
            return getattr(self.__class__, item)
        else:
            return attr


def EntryType(dn, object_classes, schema=None, *args, **kwargs):
    """Factory for creating ORM models from given object classes.

    *Creating ORM models automatically*

    :py:func:`~ldap3_orm.entry.EntryType` dynamically creates new classes
    derived from :py:class:`~ldap3_orm.entry.EntryBase` using the following
    arguments:

        - dn -- distinguished name, an unique identifier in your ldap tree
            This attribute can be defined as a template using python's built-in
            :py:func:`format` function. All class attributes and dynamically
            generated attributes defined by given ``schema`` and
            ``object_classes`` will be expanded.
        - object_classes -- one or multiple object class(es) which should be
            included in the generated model.
        - schema --
            :py:class:`ldap3_orm.Connection <ldap3.core.connection.Connection>`,
            :py:class:`~ldap3.core.server.Server` or
            :py:class:`~ldap3.procotol.rfc4512.SchemaInfo` which will be used
            to generate the model from the corresponding schema information.

    Furthermore all arguments which can be passed either as a positional
    argument or as keyword argument to
    :py:class:`~ldap3.abstract.objectDef.ObjectDef` can be passed to this
    :py:func:`~ldap3_orm.entry.EntryType`.

    *Example*::

        InetUser = EntryType("uid={uid},ou=People," + config.base_dn,
                             "inetUser", conn)

        >>> u = InetUser(uid="guest",
                         userPassword="{SSHA}oKJYPtoC+8mPBn/f47cSK5xWJuap183E")

        >>> InetUser
        OBJ : inetUser
        DN  : uid={uid},ou=People,dc=example,dc=com
        MUST:
        MAY : inetUserHttpURL, inetUserStatus, memberOf, uid, userPassword

        >>> u
        DN: uid=guest,ou=People,dc=example,dc=com
            objectClass: inetUser
            uid: guest
            userPassword: {SSHA}oKJYPtoC+8mPBn/f47cSK5xWJuap183E

    """
    attrdefs = dict(ObjectDef(object_classes, schema, *args,
                              **kwargs)._attributes)
    del attrdefs["objectClass"]
    attributes = dict(
        dn=dn,
        object_classes=tolist(object_classes),
        _attrdefs=attrdefs,
    )
    return type(fmt_class_name(object_classes), (EntryBase,), attributes)
