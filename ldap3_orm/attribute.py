# coding: utf-8

from os import linesep
from functools import wraps

# pylint: disable=unused-import
from ldap3 import ALL_ATTRIBUTES
from ldap3.abstract.attrDef import AttrDef as _AttrDef
from ldap3.utils.conv import escape_filter_chars
from ldap3_orm.pycompat import string_types
# pylint: disable=unused-import
# pylint: disable=protected-access
# noinspection PyProtectedMember
from ldap3_orm._version import __version__, __revision__


__author__ = "Christian Felder <webmaster@bsm-felder.de>"
__copyright__ = """Copyright 2016-2018, Christian Felder

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


def generative(func):
    """Mark a method as generative.

    Generative methods must implement a :py:method:`_clone()` method which
    creates a copy of ``self`` which is internally passed to the
    decorated method to ensure the calling object is not modified.

    The generative method should modify the newly created object ``self``
    which is automatically returned at the end of this method. This allows
    daisy chaining generative method calls.

    """
    @wraps(func)
    def new_func(*args, **kwargs):
        self = args[0]._clone()
        func(self, *args[1:], **kwargs)
        return self
    return new_func


def compiled_filter(func):
    """Passes a compiled and escaped filter to the decorated method."""
    @wraps(func)
    def new_func(self, other, *args, **kwargs):
        if isinstance(other, OperatorAttrDef):
            other = other.compiled_filter()
        elif isinstance(other, string_types):
            other = escape_filter_chars(other)
        return func(self, other, *args, **kwargs)
    return new_func


class AttrDef(_AttrDef):

    def __init__(self, *args, **kwargs):
        mandatory = kwargs.pop("mandatory", True)
        _AttrDef.__init__(self, *args, mandatory=mandatory, **kwargs)


class OperatorAttrDef(AttrDef):
    """Define operators for :py:class:`~ldap3.abstract.attrDef.AttrDef`
    expressions.

    Class attributes of type :py:class:`~ldap3.abstract.attrDef.AttrDef`
    specified on ORM models derived from :py:class`~ldap3_orm.entry.EntryBase`
    will automatically be promoted to this class.

    """

    _filter = ""

    @generative
    def _comparison_operator(self, other):
        filt = "({}={})".format(self.key, other)
        if self._filter:
            return self & filt
        self._filter = filt

    @compiled_filter
    def __eq__(self, other):
        return self._comparison_operator(other)

    @compiled_filter
    def startswith(self, other):
        other = "{}*".format(other)
        return self._comparison_operator(other)

    @compiled_filter
    def endswith(self, other):
        other = "*{}".format(other)
        return self._comparison_operator(other)

    @generative
    def _combine_operator(self, other, op='&'):
        if self._filter:
            self._filter = "({}{}{})".format(op, self._filter, other)
        else:
            self._filter = other

    @compiled_filter
    def __and__(self, other):
        return self._combine_operator(other, op='&')

    @compiled_filter
    def __or__(self, other):
        return self._combine_operator(other, op='|')

    def compiled_filter(self):
        return self._filter

    def __str__(self):
        return self.compiled_filter()

    def __repr__(self):
        filt = self.compiled_filter()
        if filt:
            r = AttrDef.__repr__(self)
            rfilt = " - filter: " + filt
            splitted = r.split(linesep, 1)
            if len(splitted) > 1:
                return splitted[0] + rfilt + linesep + splitted[1]
            return r + rfilt
        return AttrDef.__repr__(self)

    @classmethod
    def create_from_AttrDef(cls, attrdef):
        o = OperatorAttrDef.__new__(OperatorAttrDef)
        o.__dict__ = attrdef.__dict__.copy()
        return o

    def _clone(self):
        o = self.__class__.__new__(self.__class__)
        o.__dict__ = self.__dict__.copy()
        return o
