#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import json as JSON
import threading
from time import sleep
from PyQt4.QtCore import *

# sys.path.append('../')
from util.util import new_id
from lib.netstream import netstream, NET_STATE_ESTABLISHED, NET_STATE_STOP
PORT = 8888
HOST = '127.0.0.1'
logger = logging
# logging.basicConfig(filename='example.log', level=logging.DEBUG)


SERVICE_ID = new_id()
LOGIN_METHOD_ID = new_id()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Client(object):
    __metaclass__ = Singleton   # ref:https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python

    def __init__(self):
        self.c = netstream()
        self.start = self.is_scheduler_start = False
        self.receiver = threading.Thread(target=self.receiver)
        self.receiver.daemon = True
        self.scheduler = threading.Thread(target=self.scheduler)
        self.scheduler.daemon = True
        self.callback = {}
        self.periodic_task = []
        self.periodic_task_callback = {}

    def connect(self, adr='127.0.0.1', port=8888):
        ret = self.c.connect(adr, port)
        logger.debug('connect %s, %d %d', adr, port, ret)
        if ret == 0:
            self.receiver.start()
            self.scheduler.start()
            return 0
        return -1

    def scheduler(self):
        self.is_scheduler_start = True
        while self.is_scheduler_start:
            try:
                sleep(1)
            except Exception:
                logging.exception()
                break;
            self.handle_periodic_task()

    def receiver(self):
        self.start = True
        while self.start:
            try:
                sleep(0.1)  # time module has been collected
            except Exception:
                logging.exception()
                break
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
                        print(msg)
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

# TODO: implement a scheduler to periodically run task in different timeout
    def set_periodic_task(self, task, params, callback, task_id):
        '''
        All task run in the same frequency
        :param params: tuple
        :param task: callable
        :param callback: callable
        :param task_id: str
        :return: None
        '''
        assert callable(task) and callable(callback)
        assert isinstance(params, tuple)
        # logger.debug("-----%s %s", str(task_id), str(self.callback.keys()))
        if task_id not in self.callback.keys():
            self.callback[task_id] = callback
        self.periodic_task.append((task, params))

    def handle_periodic_task(self):
        # print("------%d", len(self.periodic_task))
        for (task, param) in self.periodic_task:
            logger.debug("handle_periodic: %s", task)
            task(*param)

    @staticmethod
    def generate_periodic_task_id(func):
        return 'poll_' + str(func.__name__)

    def send(self, service_name, method, msg):
        self.c.send('{}\r\n{}\r\n{}'.format(service_name, method, JSON.dumps(msg)))

    def register(self, key, callback):
        if not callable(callback):
            raise AssertionError()
        self.callback[key] = callback

    def close(self):
        self.is_scheduler_start = False
        self.start = False
        self.c.close()
