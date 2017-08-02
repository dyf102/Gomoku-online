#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import json as JSON
import redis

sys.path.append('../lib')
sys.path.append('../util')
from netstream import nethost, NET_NEW, NET_DATA
from util import eprint, print_trace_exception

HOST = '0.0.0.0'
PORT = 8888
logger = logging  # .getLogger('tcpserver')
logging.basicConfig(filename='example.log', level=logging.DEBUG)
DELIMINATOR = '\r\n'
r = redis.StrictRedis(host='localhost', port=6379, db=0)


class Server(object):

    def __init__(self, addr=HOST):
        self._addr = addr
        self._host = nethost(addr)
        self._handlers = {'exit': self.stop}
        self._is_started = False
        self._content_decoder = JSON.loads
        self._content_encoder = JSON.dumps
        self.at_entry = None
        self.at_exit = None

    def bind(self, port=PORT):
        self._port = port
        self._host.startup(port)

    def set_handler(self, method, func):
        if not isinstance(method, basestring) or not callable(func):
            raise AssertException()
        self._handlers[method] = func

    def listen(self):
        self._is_started = True
        logger.debug('Server starts at %s:%s', self._addr, self._port)
        while self._is_started:
            self._host.process()
            event, wparam, lparam, data = self._host.read()
            if event < 0:
                continue
            logger.debug('event=%d wparam=%xh lparam=%xh data="%s"',
                         event, wparam, lparam, data)
            if event == NET_DATA:
                idx = data.find(DELIMINATOR)
                if idx == -1:
                    logger.debug('The format of request is unexpected')
                method = data[:idx]
                content = data[idx + len(DELIMINATOR):]
                self._host.send(wparam, self._handle(wparam, method, content))
            elif event == NET_NEW:
                if self.at_entry:
                    self.at_entry(wparam)  # client id
                host.send(wparam, 'HELLO CLIENT %X' % (wparam))
                host.settag(wparam, wparam)
                host.nodelay(wparam, 1)
            elif event == NET_LEAVE and self.at_exit:
                self.at_exit(wparam)  # client id

    def _handle(self, client_id, method, content):
        try:
            func = self._handlers[method]
        except KeyError:
            logger.debug('The method is not support %s', method)
            return 'Method Not Exist: %s' % (method)
        except Exception as e:
            printTraceException()
            return '500'
        try:
            ret = func(self._content_decoder(client_id, content))
            return self._content_encoder(ret)
        except Exception as e:
            printTraceException()
        return '500'

    def set_at_entry(sefl, func):
        if not callable(func):
            raise AssertException()
        self.at_entry = func

    def set_at_exit(self, func):
        if not callable(func):
            raise AssertException()
        self.at_exit = func

    def stop(self):
        self._is_started = False

    def get_clients(self):
        return self._host.get_clients()


class Application(object):

    def __init__(self):
        self.server = Server()
        self.current_user = {}
        self.current_idle_user = {}

    def add_login_signout(self):

        def login(client_id, user_info):
            self.current_user[client_id] = user_info
            self.current_idle_user[client_id] = user_info

        def signout(client_id):
            self.current_user[client_id] = None
            self.current_idle_user[client_id] = None
        self.server.set_handler('login', login)
        self.server.set_at_exit(signout)

    def add_get_idle_user(self):
        def get_idle_list(_, _):
            return self.current_idle_user
        self.server.set_handler('get_idle_list',get_idle_list)

    def run(self):
    	self.server.bind()
    	self.listem()

def main():
    game = Application()
    game.run()

if __name__ == '__main__':
    main()
