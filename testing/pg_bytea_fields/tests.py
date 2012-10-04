# -*- coding: utf-8 -*-

from django.test import TestCase
from djorm_pgbytea.fields import ByteaField, LargeObjectProxy

from .models import ByteaModel, LargeObjectModel

import hashlib
import os.path
import io



class ByteaFieldTest(TestCase):
    def setUp(self):
        ByteaModel.objects.all().delete()

    def test_internals_field(self):
        field = ByteaField()
        prep_value = field.get_db_prep_value(None, None)
        self.assertEqual(prep_value, None)

    def test_simple_insert(self):
        path = os.path.join(os.path.dirname(__file__), "test.jpg")
        data = ''

        with io.open(path, "rb") as f:
            data = f.read()

        strhash = hashlib.sha256(data).hexdigest()
        obj = ByteaModel.objects.create(data=data)
        obj = ByteaModel.objects.get(pk=obj.id)
        self.assertEqual(strhash, hashlib.sha256(obj.data).hexdigest())

    def test_insert_void(self):
        obj = ByteaModel.objects.create(data=None)
        obj = ByteaModel.objects.get(pk=obj.id)
        self.assertEqual(obj.data, None)


class LargeObjectTest(TestCase):
    def setUp(self):
        LargeObjectModel.objects.all().delete()

    def test_create_void(self):
        LargeObjectModel.objects.create(lobj=None)

    def test_create_invalid(self):
        with self.assertRaises(ValueError):
            LargeObjectModel.objects.create(lobj=LargeObjectProxy())

    def test_write_simple_object(self):
        lobj = LargeObjectProxy()
        lobj.open()

        path = os.path.join(os.path.dirname(__file__), "test.jpg")

        with io.open(path, "rb") as f:
            lobj.write(f.read())
            lobj.close()

        instance = LargeObjectModel.objects.create(lobj=lobj)
        instance = LargeObjectModel.objects.get(pk=instance.pk)

        with io.open(path, "rb") as f:
            original_data = f.read()

            instance.lobj.open()
            database_data = instance.lobj.read()

            self.assertEqual(original_data, database_data)
