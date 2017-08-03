#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import json as JSON
import threading
from time import sleep

sys.path.append('../lib')
sys.path.append('../util')

from util import new_id
from netstream import netstream, NET_STATE_ESTABLISHED, NET_STATE_STOP
PORT = 8888
HOST = '127.0.0.1'
logger = logging  # .getLogger('tcpserver')
logging.basicConfig(filename='example.log', level=logging.DEBUG)


SERVICE_ID = new_id()
LOGIN_METHOD_ID = new_id()


class Client(object):
    
    def __init__(self):
        self.c = netstream()
        self.start = False
        self.receiver = threading.Thread(target=self.receiver)
        self.receiver.daemon = True
        self.callback = {}
    
    def connect(self, addr='127.0.0.1', port='8888'):
        ret = self.c.connect(addr, port)
        if ret == 0:
            self.receiver.start()
            return 0
        return -1
            
    def receiver(self):
        self.start = True
        while self.start:
            sleep(0.1)
            self.c.process()
            if self.c.statue() == netstream.NET_STATE_ESTABLISHED:
                while True:
                    data = self.c.recv()
                    if data:
                        logging.debug('recv %s', data)
                        msg = JSON.loads(data)
                        _id = msg.get('id')
                        if _id is None:
                            logging.debug('no id %s', data)
                            continue
                        try:
                            self.callback[_id](data)
                        except KeyError:
                            logging.debug('unsupported id %s', data)
            elif self.status() == netstream.NET_STATE_STOP:
                pass

    def register(self, key, callback):
        if not callable(callback):
            raise AssertionError()
        self.callback[key] = callback
