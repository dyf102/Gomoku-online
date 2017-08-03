#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
import json as JSON
from network import Client
from PyQt4.QtCore import SIGNAL

GET_GAME_LIST = 'GET_GAME_LIST'
IDLE = 0


class GameLobbyController(object):
    # TODO: add singleton to controller

    def __init__(self):
        self.c = Client()

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

