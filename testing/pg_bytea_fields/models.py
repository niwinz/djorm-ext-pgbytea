# -*- coding: utf-8 -*-

from django.db import models
from djorm_pgbytea.fields import ByteaField, LargeObjectField
from djorm_pgbytea.byteafile import ByteaFileDescriptor


class ByteaModel(models.Model):
     data = ByteaField()
     datafile = ByteaFileDescriptor("data")


class LargeObjectModel(models.Model):
    lobj = LargeObjectField(default=None, null=True)
