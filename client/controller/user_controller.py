#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
import json as JSON
from network import Client
from PyQt4.QtCore import SIGNAL

LOGIN_ID = 'Login'


class UserController(object):
    # TODO: add singleton to controller

    def __init__(self):
        self.c = Client()
        self.current_user = None

    def is_login(self):
        return self.current_user is None
    
    def login(self, username):
        req = {
            'id': LOGIN_ID,
            'username': username
        }
        self.c.register(LOGIN_ID, self.login_callback)
        self.c.send(JSON.dumps(req))

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
            self.current_user = data.get('user_info')
        self.emit(SIGNAL("loginCallback(int)"), data['code'])
