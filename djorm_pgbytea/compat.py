# -*- coding: utf-8 -*-

import six
import sys

if six.PY3:
    buffer_type = (memoryview,)
else:
    if sys.platform.startswith('java'):
        buffer_type = (memoryview,)
    else:
        buffer_type = (memoryview, buffer,)
