djorm-ext-pgbytea
=================

Binary field and other usefull tools for postgresql bytea field type.

Simple example:

.. code-block:: python

    from django.db import models
    from djorm_pgbytea.fields import ByteaField, LargeObjectField

    class ByteaModel(models.Model):
        data = ByteaField()

    class LargeObjectModel(models.Model):
        lobj = LargeObjectField(default=None, null=True)


How to install?
---------------

Install the stable version using pip by running:

.. code-block:: bash

    pip install djorm-ext-pgbytea
