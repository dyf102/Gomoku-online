#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import traceback
import logging

logger = logging
def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

def print_trace_exception():
	exc_type, exc_value, exc_traceback = sys.exc_info()
	traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stderr)