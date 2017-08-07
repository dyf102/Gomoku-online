#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
import os
# import json as JSON
from PyQt4.QtCore import SIGNAL, QObject, QString
from basecontroller import BaseController, singleton
from controller.game_controller import GameController

LOGIN_ID = 'LOGIN'
GET_RANK_ID = 'GET_USER_RANK'

SERVICE_NAME = 'UserService'


@singleton
class UserController(BaseController):

    def __init__(self):
        BaseController.__init__(self, SERVICE_NAME)
        self.current_username = None
        self.current_user_id = None
        self.current_user_point = -1

        self.c.register(LOGIN_ID, self.login_callback)

        self.game_controller = GameController()

    def is_logging(self):
        return self.is_connecting

    def is_login(self):
        return self.is_connected

    def login(self, username):
        # print(username)
        client = self.get_client()
        req = {
            'username': username
        }
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
            self.current_user_id = data.get('uid')
            self.current_user_point = data.get('point')
            self.emit(SIGNAL("login_callback(int,QString)"), data['code'],
                      QString(self.current_username))
            self.is_connected = True

            self.add_polling_rank_task()
            self.game_controller.add_polling_game_list_task()
        except KeyError:
            logging.debug('Login Callback data is None %s', data)

    def add_polling_rank_task(self):
        c = self.get_client()
        c.set_periodic_task(self.get_user_rank, (), self.get_user_rank_callback, GET_RANK_ID)

    def get_user_rank(self):
        client = self.get_client()
        req = {
            'uid': self.current_user_id
        }
        client.send(SERVICE_NAME, GET_RANK_ID, req)

    def get_user_rank_callback(self, data):
        if data and data.get('code') == 200:
            try:
                user_list = data['list']
            except KeyError:
                logging.debug("get_rank: %s ", data)
            else:
                self.emit(SIGNAL('clear'))
                for user in user_list:
                    username = user.get('username')
                    point = user.get('point')
                    self.emit(SIGNAL('add_rank_item(QString, int)'), username, point)
        else:
            logging.debug("get_user_rank_callback: %s", data)
