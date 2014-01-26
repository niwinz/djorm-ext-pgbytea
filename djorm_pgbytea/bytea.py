# -*- coding: utf-8 -*-

import types
import six

from django.db import models
from psycopg2 import Binary

from . import compat

psycopg_binary_class = Binary("").__class__


class ByteaField(six.with_metaclass(models.SubfieldBase, models.Field)):
    """
    Simple bytea field for save binary data
    on postgresql.

    This field does not support any django lookups
    for searching.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('blank', True)
        kwargs.setdefault('null', True)
        kwargs.setdefault('default', None)
        super(ByteaField, self).__init__(*args, **kwargs)

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'isnull':
            return super(ByteaField, self).get_prep_lookup(lookup_type, value)
        raise TypeError("This field does not allow any kind of search.")

    def get_db_prep_lookup(self, lookup_type, value, connection, prepared=False):
        if lookup_type == 'isnull':
            return super(ByteaField, self).get_db_prep_lookup(lookup_type, value,
                                                              connection=connection,
                                                              prepared=prepared)
        raise TypeError("This field does not allow any kind of search.")

    def db_type(self, connection):
        return 'bytea'

    def get_db_prep_value(self, value, connection, prepared=False):
        value = value if prepared else self.get_prep_value(value)
        if isinstance(value, six.text_type):
            value = Binary(value.encode('utf-8'))
        elif isinstance(value, six.binary_type):
            value = Binary(value)
        elif isinstance(value, psycopg_binary_class) or value is None:
            value = value
        else:
            raise ValueError("only str and bytes permited")
        return value

    def get_prep_value(self, value):
        return value

    def to_python(self, value):
        if isinstance(value, six.binary_type):
            return value
        elif isinstance(value, six.text_type):
            return value.encode('utf-8')
        elif isinstance(value, compat.buffer_type):
            if hasattr(value, "tobytes"):
                return value.tobytes()
            return six.binary_type(value)

        return value


# South support
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ['^djorm_pgbytea\.bytea\.ByteaField'])
except ImportError:
    pass
