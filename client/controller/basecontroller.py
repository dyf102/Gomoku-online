#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
import os
# import json as JSON
from network import Client
from PyQt4.QtCore import SIGNAL, QObject, QString
from PyQt4 import Qt, QtCore, QtGui
import threading
import socket
import Queue
import time

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
        self.is_connecting = False
        self.is_connected = False
        self.service_name = service_name
        self.connector = SafeConnector()
        self.c = Client()

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
# Object of this class has to be shared between
# the two threads (Python and Qt one).
# Qt thread calls 'connect',
# Python thread calls 'emit'.
# The slot corresponding to the emitted signal
# will be called in Qt's thread.


class SafeConnector:
    def __init__(self):
        self._rsock, self._wsock = socket.socketpair()
        self._queue = Queue.Queue()
        self._qt_object = QtCore.QObject()
        self._notifier = QtCore.QSocketNotifier(self._rsock.fileno(),
                                                QtCore.QSocketNotifier.Read)
        self._notifier.activated.connect(self._recv)

    def connect(self, signal, receiver):
        QtCore.QObject.connect(self._qt_object, signal, receiver)

    # should be called by Python thread
    def emit(self, signal, *args):
        self._queue.put((signal, args))
        self._wsock.send('!')

    # happens in Qt's main thread
    def _recv(self):
        self._rsock.recv(1)
        signal, args = self._queue.get()
        self._qt_object.emit(signal, *args)




