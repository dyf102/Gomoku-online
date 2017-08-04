#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
import os
import json as JSON
from network import Client
from PyQt4.QtCore import SIGNAL, QObject, QString
sys.path.append('../')
from util.util import print_trace_exception

LOGIN_ID = 'LOGIN'
SERVICE_NAME = 'UserService'

class UserController(QObject):
    # TODO: add singleton to controller

    def __init__(self):
        QObject.__init__(self)
        self.c = Client()
        self.current_user = None
        self.is_connecting = False
        self.is_connected = False

    def connect_client(self, addr, port):
        if not (self.is_connected or self.is_connecting):
            self.is_connecting = True
            ret = self.c.connect(addr, port)
            print(ret)
            if ret == -1:
                self.is_connecting = False
                print_trace_exception()
                raise os.ConnectionError()
            self.is_connected = True
            self.is_connecting = False

    def is_logging(self):
        return self.is_connecting

    def is_login(self):
        return self.is_connected

    def login(self, username):
        # print(username)
        req = {
            'id': LOGIN_ID,
            'username': username
        }
        self.c.register(LOGIN_ID, self.login_callback)
        self.c.send(SERVICE_NAME, LOGIN_ID, req)

    def login_callback(self, data):
        '''
        {
        uid: "",
        code: "",
        }
        :param data:
        :return:
        '''

        logging.debug('Login Callback %s', data)
        if data.get('uid') is None:
            logging.debug('Login Callback data is None %s', data)
        else:
            self.current_user = data.get('uinfo')
            self.emit(SIGNAL("login_callback(int,QString)"), data['code'],
                      QString(self.current_user.get('username')))
            self.is_connected = True

