# coding: utf-8

from os import linesep

from ldap3.abstract.attrDef import AttrDef
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
    def new_func(*args, **kwargs):
        self = args[0]._clone()
        func(self, *args[1:], **kwargs)
        return self
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    return new_func


def compiled_filter(func):
    def new_func(self, other, *args, **kwargs):
        if isinstance(other, OperatorAttrDef):
            other = other.compiled_filter()
        elif isinstance(other, string_types):
            other = escape_filter_chars(other)
        return func(self, other, *args, **kwargs)
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    return new_func


class OperatorAttrDef(AttrDef):

    _filter = ""

    @generative
    @compiled_filter
    def __eq__(self, other):
        filt = "({}={})".format(self.key, other)
        if self._filter:
            return self & filt
        self._filter = filt

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

    def _clone(self):
        o = self.__class__.__new__(self.__class__)
        o.__dict__ = self.__dict__.copy()
        return o
