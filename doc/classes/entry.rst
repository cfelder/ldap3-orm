****************
ldap3-orm module
****************

This module provides classes for creating object-relational mappings for
LDAP data. In particular it provides the base class
:py:class:`~ldap3_orm.entry.EntryBase` which uses class attributes in order to
configure the *ORM model* and dynamically creates a appropriate constructor
with the objective of writing less code and to focus on the configuration.

API Reference
=============

.. module:: ldap3_orm

.. autoclass :: ParamDef
   :members:

.. autoclass :: EntryBase
   :members:
