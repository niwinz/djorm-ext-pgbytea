djorm-ext-pgbytea
=================

Binary field and other usefull tools for postgresql bytea field type.

Simple example::

    from django.db import models
    from djorm_pgbytea.fields import ByteaField, LargeObjectField

    class ByteaModel(models.Model):
        data = ByteaField()

    class LargeObjectModel(models.Model):
        lobj = LargeObjectField(default=None, null=True)
