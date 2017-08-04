#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import json as JSON
import redis

sys.path.append('../')
from lib.netstream import nethost, NET_NEW, NET_DATA, NET_LEAVE
from util.util import eprint, print_trace_exception, new_id

HOST = '0.0.0.0'
PORT = 8888
logger = logging  # .getLogger('tcpserver')
logging.basicConfig(filename='example.log', level=logging.DEBUG)
DELIMINATOR = '\r\n'
r = redis.StrictRedis(host='localhost', port=6379, db=0)

'''
NET_NEW =        0    # new connection£º(id,tag) ip/d,port/w   <hid>
NET_LEAVE =        1    # lost connection£º(id,tag)           <hid>
NET_DATA =        2    # data comming£º(id,tag) data...    <hid>
NET_TIMER =        3    # timer event: (none, none) 
'''


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
        assert isinstance(method, basestring) and callable(func)
        self._handlers[method] = func

    def listen(self):
        self._is_started = True
        logger.debug('Server starts at %s:%s', self._addr, self._port)
        wparam = 0
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
                # self._host.send(wparam, "hello")
                self._host.send(wparam, self._handle(wparam, method, content))
                # self._host.settag(wparam, wparam)
                # self._host.nodelay(wparam, 1)
                logger.debug('End of Send')
            elif event == NET_NEW:
                if self.at_entry:
                    self.at_entry(wparam)  # client id
                # self._host.send(wparam, 'HELLO CLIENT %X' % (wparam))
                # self._host.settag(wparam, wparam)
                # self._host.nodelay(wparam, 1)
            elif event == NET_LEAVE and self.at_exit:
                self.at_exit(wparam)  # client id
        self._host.send(wparam,'quit')

    def _handle(self, client_id, method, _str):
        try:
            func = self._handlers[method]
            logger.debug('Return function: %s', str(func))
        except KeyError:
            logger.debug('The method is not support %s', method)
            return 'Method Not Exist: %s' % (method)
        except Exception as e:
            print(e)
            print_trace_exception()
            return '500'
        try:
            ret = func(client_id, self._content_decoder(_str))
            logger.debug('Return %s', self._content_encoder(ret))
            return self._content_encoder(ret)
        except Exception:
            logger.debug('The method is not support 2 %s', method)
            print_trace_exception()
        return '500'

    def set_at_entry(self, func):
        assert callable(func) == True
        self.at_entry = func

    def set_at_exit(self, func):
        assert callable(func) == True
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
        self.add_login_signout()

    def add_login_signout(self):
        _id = 'LOGIN'

        def login(client_id, user_info):
            self.current_user[client_id] = user_info
            self.current_idle_user[client_id] = user_info
            return {'id': _id, 'code': 200, 'uid': client_id, 'uinfo': user_info}
        
        def signout(client_id):
            self.current_user[client_id] = None
            self.current_idle_user[client_id] = None
        
        self.server.set_handler(_id, login)
        self.server.set_at_exit(signout)

    def add_get_idle_user(self):
        def get_idle_list(_):
            return self.current_idle_user
        self.server.set_handler('get_idle_list', get_idle_list)

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
