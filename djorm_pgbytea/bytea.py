# -*- coding: utf-8 -*-

from django.db import models
from psycopg2 import Binary
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

