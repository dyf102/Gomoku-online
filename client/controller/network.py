#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import json as JSON
import threading
from time import sleep

sys.path.append('../')

from util.util import new_id
from lib.netstream import netstream, NET_STATE_ESTABLISHED, NET_STATE_STOP
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
    
    def connect(self, addr='127.0.0.1', port=8888):
        ret = self.c.connect(addr, port)
        print(addr, port, ret)
        if ret == 0:
            self.receiver.start()
            return 0
        return -1
            
    def receiver(self):
        self.start = True
        while self.start:
            sleep(0.1)
            self.c.process()
            if self.c.status() == NET_STATE_ESTABLISHED:
                while True:
                    data = self.c.recv()
                    if data:
                        logging.debug('recv %s', data)
                        try:
                            msg = JSON.loads(data)
                        except ValueError:
                            logging.debug('JSON FORMAT Exception %s', data)
                        _id = msg.get('id')
                        if _id is None:
                            logging.debug('no id %s', data)
                            continue
                        try:
                            obj = JSON.loads(data)
                            func = self.callback[_id]

                        except KeyError as e:
                            logging.debug('unsupported id: %s', data)
                            raise e
                        except ValueError as e:
                            logging.debug('Invalid Format: %s', data)
                            raise e
                        else:
                            func(obj)
            elif self.c.status() == NET_STATE_STOP:
                pass

    def send(self, key, msg):
        self.c.send('{}\r\n{}'.format(key, JSON.dumps(msg)))

    def register(self, key, callback):
        if not callable(callback):
            raise AssertionError()
        self.callback[key] = callback
