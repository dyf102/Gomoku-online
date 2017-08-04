#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import json as JSON
import redis
from server import Server

from service.user_service import UserService, BaseService
sys.path.append('../')



class Application(object):

    def __init__(self):
        self.server = Server()
        self.hub = {}
        self.register(UserService())

    def register(self, service):
        assert isinstance(BaseService)
        name = service.user_service
        self.hub[name] = service.get_handler

    def run(self):
        self.server.bind()
        try:
            self.server.listen()
        except KeyboardInterrupt as k:
            self.server.stop()
            raise k

def main():
    game = Application()
    game.run()

if __name__ == '__main__':
    main()
