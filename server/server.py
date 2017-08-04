import sys
import logging
import json as JSON
import redis

from lib.netstream import nethost, NET_NEW, NET_DATA, NET_LEAVE
from util.util import eprint, print_trace_exception, new_id
from lib.singleton import Singleton
HOST = '0.0.0.0'
PORT = 8888
formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                              '%m-%d %H:%M:%S')
logger = logging
logging.basicConfig(filename='example.log', level=logging.DEBUG, format=formatter)

DELIMINATOR = '\r\n'
r = redis.StrictRedis(host='localhost', port=6379, db=0)

'''
NET_NEW =        0    # new connection
NET_LEAVE =        1    # lost connection
NET_DATA =        2    # data come
NET_TIMER =        3    # timer event: (none, none) 
'''


class Server(Singleton):

    def __init__(self, adr=HOST):
        self._addr = adr
        self._host = nethost(adr)
        self._handlers = {'exit': self.stop}
        self._is_started = False
        self._content_decoder = JSON.loads
        self._content_encoder = JSON.dumps
        self._at_entry = None
        self._at_exit = None
        self._port = None

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
                self._host.send(wparam, self._handle(wparam, method, content))
                logger.debug('End of Send')
            elif event == NET_NEW:
                if self._at_entry:
                    self._at_entry(wparam)  # client id
            elif event == NET_LEAVE and self._at_exit:
                self._at_exit(wparam)  # client id
        self._host.send(wparam, 'quit')

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
        assert callable(func) is True
        self._at_entry = func

    def set_at_exit(self, func):
        assert callable(func) is True
        self._at_exit = func

    def stop(self):
        self._is_started = False

    def get_clients(self):
        return self._host.get_clients()