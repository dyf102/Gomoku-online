#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
import json as JSON
from network import Client
from PyQt4.QtCore import SIGNAL, QObject, QString, pyqtSignal
from basecontroller import BaseController

SERVICE_NAME = 'GameService'
GET_GAME_LIST_ID = "GET_GAME_LIST"


class GameController(BaseController):
    game_list_signal = pyqtSignal(unicode)

    def __init__(self):
        BaseController.__init__(self, service_name=SERVICE_NAME)
        self.game_list = None
        # self.c.register(GET_GAME_LIST_ID, self.get_game_list_callback)

    def add_polling_game_list_task(self):
        client = self.get_client()
        client.set_periodic_task(self.get_game_list, (), self.get_game_list_callback, GET_GAME_LIST_ID)

    def get_game_list(self):
        req = {}
        client = self.get_client()
        client.send(service_name=SERVICE_NAME, method=GET_GAME_LIST_ID, msg=req)

    def get_game_list_callback(self, data):
        if data and data.get('code') == 200:
            game_list = data.get(u'list')
            logging.debug("get_game_list_callback %s", game_list)
            self.game_list = game_list
            self.connector.emit(SIGNAL('game_list_clear'))
            for game in game_list:
                txt = '{} vs {}'.format(game.get('host_name'), game.get('guest_name'))
                id = game.get('id')
                if id is None:
                    logging.debug("Invalid format %s", game)
                    continue
                self.connector.emit(SIGNAL('game_list'), QString(txt), QString(id))
                logging.debug("ret : %s", txt)

    def testEmit(self):
        self.game_list_signal.emit(unicode('123'))