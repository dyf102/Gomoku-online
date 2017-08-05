#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import traceback
import logging
import uuid
from functools import wraps
logger = logging


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def print_trace_exception():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stderr)


def new_id():
    return str(uuid.uuid4())


def log_callback(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.debug("callback func:%s recieved: %s", func.__name__, kwargs.get('data') )
        ret = func(*args, **kwargs)
        logging.debug("callback func:%s return: %s", func.__name__, ret)
        return ret
    return wraps