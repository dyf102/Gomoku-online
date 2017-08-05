#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
import os
# import json as JSON
from PyQt4.QtCore import SIGNAL, QObject, QString
from basecontroller import BaseController


LOGIN_ID = 'LOGIN'
SERVICE_NAME = 'UserService'


class UserController(BaseController):

    def __init__(self):
        BaseController.__init__(self, SERVICE_NAME)
        self.current_username = None
        self.current_user_id = None
        self.current_user_point = -1

    def is_logging(self):
        return self.is_connecting

    def is_login(self):
        return self.is_connected

    def login(self, username):
        # print(username)
        client = self.get_client()
        req = {
            'id': LOGIN_ID,
            'username': username
        }
        client.register(LOGIN_ID, self.login_callback)
        client.send(SERVICE_NAME, LOGIN_ID, req)

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
        try:
            self.current_username = data.get('username')
            self.current_user_id = data['uid']
            self.current_user_point = data.get('point')
            self.emit(SIGNAL("login_callback(int,QString)"), data['code'],
                      QString(self.current_username))
            self.is_connected = True
        except KeyError:
            logging.debug('Login Callback data is None %s', data)
