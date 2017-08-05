import sys
import logging
import json as JSON
import redis

sys.path.append('../')
from lib.netstream import nethost, NET_NEW, NET_DATA, NET_LEAVE
from util.util import print_trace_exception
from lib.singleton import Singleton
HOST = '0.0.0.0'
PORT = 8888
fmt = "[%(filename)s:%(lineno)s] %(message)s"
#formatter = logging.Formatter(fmt)
logger = logging
logging.basicConfig(filename='example.log',
                    level=logging.DEBUG, format=fmt)

DELIMINATOR = '\r\n'
r = redis.StrictRedis(host='localhost', port=6379, db=0)

'''
NET_NEW =        0    # new connection
NET_LEAVE =        1    # lost connection
NET_DATA =        2    # data come
NET_TIMER =        3    # timer event: (none, none) 
'''


class Server(Singleton):

    def __init__(self, adr=HOST, dispatch=None):
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

    def listen(self, dispatch):
        self._is_started = True
        self.dispatch = dispatch
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
                ret = self._handle(wparam, data)
                self._host.send(wparam, ret)
                logger.debug('End of Send %s', ret)
            elif event == NET_NEW:
                if self._at_entry:
                    self._at_entry(wparam)  # client id
            elif event == NET_LEAVE and self._at_exit:
                self._at_exit(wparam)  # client id
        self._host.send(wparam, 'quit')

    def _handle(self, uid, data):
        items = data.split(DELIMINATOR)
        if len(items) < 3:
            logger.debug('The format of request is unexpected')
        service, method = items[0], items[1]
        raw_data = DELIMINATOR.join(items[2:])
        try:
            data = self._content_decoder(raw_data)
        except JSON.JSONDecodeError:
            logging.debog("Unenable decode JSON Data %s", raw_data)
            return self.sendError(400, '1')
        try:
            func = self.dispatch(service, method)
            ret_obj = func(uid, data)
        except Exception as e:
            print_trace_exception()
            logger.exception(str(e))
            return self.sendError(500, '2')
        try:
            ret = JSON.dumps(ret_obj)
            return ret
        except JSON.JSONEncoderError:
            print_trace_exception()
            logging.debog("Unenable encode Data to JSON %s", raw_data)
            return self.sendError(500, '3')
        print("--" * 10)
    def sendError(self, code, msg):
        return JSON.dumps({'code': code, 'msg': msg})

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
