# -*- coding: utf-8 -*-

import types
import sys

from django.db import models, connections

try:
    from django.utils import six
except ImportError:
    import six

from psycopg2.extensions import lobject as lobject_class


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
        elif value is None:
            return None

        raise ValueError("Invalid value")

    def get_prep_value(self, value):
        return value

    def to_python(self, value):
        if isinstance(value, LargeObjectFile):
            return value
        elif isinstance(value, six.integer_types):
            return LargeObjectFile(value, self, self.model)
        elif value is None:
            return None

        raise ValueError("Invalid value")
