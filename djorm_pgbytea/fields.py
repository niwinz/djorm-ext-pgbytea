# -*- coding: utf-8 -*-

from django.db import models, connections
from psycopg2 import Binary
from psycopg2.extensions import lobject as lobject_class
import types

psycopg_bynary_class = Binary("").__class__


class ByteaField(models.Field):
    """
    Simple bytea field for save binary data
    on postgresql.

    This field does not support any django lookups
    for searching.
    """

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('blank', True)
        kwargs.setdefault('null', True)
        kwargs.setdefault('default', None)
        super(ByteaField, self).__init__(*args, **kwargs)

    def get_prep_lookup(self, lookup_type, value):
        raise TypeError("This field does not allow any kind of search.")

    def get_db_prep_lookup(self, lookup_type, value, connection, prepared=False):
        raise TypeError("This field does not allow any kind of search.")

    def db_type(self, connection):
        return 'bytea'

    def get_db_prep_value(self, value, connection, prepared=False):
        value = value if prepared else self.get_prep_value(value)
        if isinstance(value, unicode):
            value = Binary(value.encode('utf-8'))
        elif isinstance(value, str):
            value = Binary(value)
        elif isinstance(value, (psycopg_bynary_class, types.NoneType)):
            value = value
        else:
            raise ValueError("only str, unicode and bytea permited")
        return value

    def get_prep_value(self, value):
        return value

    def to_python(self, value):
        if isinstance(value, str):
            return value
        elif isinstance(value, unicode):
            return value.encode('utf-8')
        elif isinstance(value, buffer):
            return str(value)

        return value


class LargeObjectFile(object):
    """
    Proxy class over psycopg2 large object file instance.
    """
    def __init__(self, oid=0, field=None, instance=None, **params):
        self.oid = oid
        self.field = field
        self.instance = instance
        self.params = params
        self._obj = None

    def __getattr__(self, name):
        if self._obj is None:
            raise Exception("File is not opened")
        try:
            return super(LargeObjectFile, self).__getattr__(name)
        except AttributeError:
            return getattr(self._obj, name)

    def open(self, mode="rwb", new_file=None, using="default"):
        connection = connections[using]
        self._obj = connection.connection.lobject(self.oid, mode, 0, new_file)
        self.oid = self._obj.oid
        return self


class LargeObjectDescriptor(models.fields.subclassing.Creator):
    """
    LargeObjectField descriptor.
    """

    def __set__(self, instance, value):
        value = self.field.to_python(value)
        if value is not None:
            if not isinstance(value, LargeObjectFile):
                value = LargeObjectFile(value, self.field, instance)
        instance.__dict__[self.field.name] = value


class LargeObjectField(models.IntegerField):
    """
    LargeObject field.

    Internally is an ``oid`` field but returns a proxy
    to referenced file.
    """

    def db_type(self, connection):
        return 'oid'

    def contribute_to_class(self, cls, name):
        super(LargeObjectField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, LargeObjectDescriptor(self))

    def _value_to_python(self, value):
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)

        if isinstance(value, LargeObjectFile):
            if value.oid > 0:
                return value.oid

            raise ValueError("Oid must be a great that 0")

        elif isinstance(value, types.NoneType):
            return None

        raise ValueError("Invalid value")

    def get_prep_value(self, value):
        return value

    def to_python(self, value):
        if isinstance(value, LargeObjectFile):
            return value
        elif isinstance(value, (int, long)):
            return LargeObjectFile(value, self, self.model)
        elif isinstance(value, types.NoneType):
            return None

        raise ValueError("Invalid value")
