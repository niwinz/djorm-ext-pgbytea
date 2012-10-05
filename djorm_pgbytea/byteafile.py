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
        return self._get_current_size()

    def _get_current_size(self):
        sql = "SELECT octet_length({0}) FROM {1} WHERE {2} = %s"
        sql = sql.format(self.field_name, self._table_name, self._pk_field_name)

        cursor = connection.cursor()
        cursor.execute(sql, [self.model_instance.pk])

        result = cursor.fetchone()
        cursor.close()
        _size = result[0] if result and len(result) == 1 else 0
        if _size is None:
            return 0
        return _size

    def write(self, data):
        #import pdb; pdb.set_trace()
        assert isinstance(data, bytes), "data must be bytes"

        current_size = self._get_current_size()

        if self._position == self.size:
            sql = "UPDATE {0} SET {1} = %s WHERE {2} = %s"
            sql = sql.format(self._table_name, self.field_name, self._pk_field_name)

            cursor = connection.cursor()
            cursor.execute(sql, [memoryview(data), self.model_instance.pk])
            cursor.close()

        elif self._position + len(data) > current_size:
            sql = "UPDATE {0} SET {1} = substring({1} from 0 for %s) || %s WHERE {2} = %s;"
            sql = sql.format(self._table_name, self.field_name, self._pk_field_name)

            cursor = connection.cursor()
            cursor.execute(sql, [self._position, memoryview(data), self.model_instance.pk])
            cursor.close()

        else:
            sql = ("UPDATE {0} SET {1} = substring({1} from 1 for %s) || %s "
                   "|| substring({1} from %s for %s) WHERE {2} = %s;")

            sql = sql.format(self._table_name, self.field_name, self._pk_field_name)

            cursor = connection.cursor()
            cursor.execute(sql, [self._position, memoryview(data),
                                 self._position + len(data)+1, current_size, self.model_instance.pk])
            cursor.close()

        self._position += len(data)
        return len(data)

    def read(self, length=None):
        if length is None:
            return getattr(self, self.field_name, None)

        current_size = self._get_current_size()
        if self._position + length > current_size:
            length = current_size

        sql = "SELECT substring({0} from %s for %s) FROM {1} WHERE {2} = %s"
        sql = sql.format(self.field_name, self._table_name, self._pk_field_name)

        cursor = connection.cursor()
        cursor.execute(sql, [self._position+1, length, self.model_instance.pk])
        result = cursor.fetchone()
        cursor.close()

        return result[0] if result is not None else ""


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

