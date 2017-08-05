from service.baseservice import BaseService
from server import Server
from util.util import print_trace_exception
import logging


class Application(object):

    def __init__(self, service_list):
        self.server = Server()
        self.hub = {}
        map(lambda service: self.register(service()), service_list)

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
            # raise k

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
