# -*- coding: utf-8 -*-

from django.db import connection


class ByteaFile(object):
    _position = 0
    _size = None

    def __init__(self, model_instance, field_name):
        self.model_instance = model_instance
        self.field_name = field_name

    @property
    def _table_name(self):
        return self.model_instance._meta.db_table

    @property
    def _pk_field_name(self):
        return self.model_instance._meta.pk.name

    @property
    def size(self):
        if self._size is None:
            sql = "SELECT octet_length({0}) FROM {1} WHERE {2} = %s"
            sql = sql.format(self.field_name, self._table_name, self._pk_field_name)

            cursor = connection.cursor()
            cursor.execute(sql, [self.model_instance.pk])

            result = cursor.fetchone()
            cursor.close()
            self._size = result[0] if result and len(result) == 1 else 0
            if self._size is None:
                return 0
        return self._size

    def write(self, data):
        #import pdb; pdb.set_trace()
        assert isinstance(data, bytes), "data must be bytes"

        if self._position == 0:
            sql = "UPDATE {0} SET {1} = %s WHERE {2} = %s"
            sql = sql.format(self._table_name, self.field_name, self._pk_field_name)

            cursor = connection.cursor()
            cursor.execute(sql, [memoryview(data), self.model_instance.pk])
            cursor.close()
        else:
           sql = "UPDATE {0} SET {1} = substring({1} from 1 for %s) || %s WHERE {2} = %s;"
           sql = sql.format(self._table_name, self.field_name, self._pk_field_name)

           cursor = connection.cursor()
           cursor.execute(sql, [self._position, memoryview(data), self.model_instance.pk])
           cursor.close()

        self._position += len(data)
        return len(data)


class ByteaFileDescriptor(object):
    _file = None
    def __init__(self, field_name):
        self.field_name = field_name

    def __set__(self, instance, value):
        raise RuntimeError("Readonly attribute")

    def __get__(self, instance, owner=None):
        if self._file is None:
            self._file = ByteaFile(instance, self.field_name)
        return self._file

