#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import json as JSON
# import redis
from server import Server

from service.user_service import UserService, BaseService
from util.util import print_trace_exception
# sys.path.append('../')


class Application(object):

    def __init__(self):
        self.server = Server()
        self.hub = {}
        self.register(UserService())

    def register(self, service):
        assert isinstance(service, BaseService)
        name = service.get_name()
        self.hub[name] = service

    def run(self):
        self.server.bind()
        try:
            self.server.listen(dispatch=self.dispatch)
        except KeyboardInterrupt as k:
            self.server.stop()
            raise k

    def dispatch(self, service_name, method):
        try:
            #logging.debug('service_name %s', service_name)
            #logging.debug('hub %s', self.hub)
            handlers = self.hub[service_name]
        except KeyError as e:
            logging.debug('Key not found: %s', service_name)
            print_trace_exception()
            raise e
        try:
            # print(handlers.__name__, method)
            func = handlers[method]
            return func
        except KeyError as e:
            logging.debug('Method not found %s', method)
            print_trace_exception()
            raise e

def main():
    game = Application()
    game.run()

if __name__ == '__main__':
    main()
