#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
import json as JSON
from network import Client
from PyQt4.QtCore import SIGNAL
from basecontroller import BaseController

GET_GAME_LIST = 'GET_GAME_LIST'
IDLE = 0
SERVICE_NAME = 'GameService'


class GameLobbyController(BaseController):
    # TODO: add singleton to controller

    def __init__(self):
        BaseController.__init__(self, service_name=SERVICE_NAME)

    def get_game_list(self):
        pass

    def get_game_list_callback(self):
        pass

    def join_game_by_gid(self, gid):
        pass

    def leave_game_by_gid(self, gid):
        pass

    def create_game(self):
        pass

    def create_room_callback(self):
        pass

