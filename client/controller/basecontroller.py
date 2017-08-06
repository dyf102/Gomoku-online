#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
import os
# import json as JSON
from network import Client
from PyQt4.QtCore import SIGNAL, QObject, QString
sys.path.append('../')
# from util.util import print_trace_exception


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


class BaseController(QObject):
    _instance = None

    def __init__(self, service_name):
        QObject.__init__(self)
        self.c = Client()
        self.is_connecting = False
        self.is_connected = False
        self.service_name = service_name

    def connect_client(self, adr, port):
        if not (self.is_connected or self.is_connecting):
            self.is_connecting = True
            self.c.connect(adr, port)  # will not return any error code
            # if ret == -1:
            #    self.is_connecting = False
            #    print_trace_exception()
            #    raise os.ConnectionError()
            self.is_connected = True
            self.is_connecting = False

    def get_client(self):
        return self.c

