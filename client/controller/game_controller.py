#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
import json as JSON
from network import Client
from PyQt4.QtCore import SIGNAL, QObject
from basecontroller import BaseController

SERVICE_NAME = 'GameService'
GET_GAME_LIST_ID = "GET_GAME_LIST"


class GameController(BaseController):

    def __init__(self):
        BaseController.__init__(self, service_name=SERVICE_NAME)

    def add_polling_game_list_task(self):
        client = self.get_client()
        client.set_periodic_task(self.get_game_list, (), self.get_game_list_callback, GET_GAME_LIST_ID)

    def get_game_list(self):
        req = {}
        client = self.get_client()
        client.send(service_name=SERVICE_NAME, method=GET_GAME_LIST_ID, msg=req)

    def get_game_list_callback(self, data):
        if data and data.get('code') == 200:
            game_list = data.get('list')
            logging.debug("get_game_list_callback %s", game_list)

