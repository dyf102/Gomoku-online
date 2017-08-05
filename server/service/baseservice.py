from functools import wraps
from util.util import print_trace_exception

class ServiceException(Exception):
    pass


class ServiceHandlerMissingException(ServiceException):
    pass


def register(_self):
    def outter_wrapper(func):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            _self.add_handler(func)
            return func(*args, **kwargs)
        return inner_wrapper
    return outter_wrapper


def handler(func):
    _id = BaseService.get_id(func)

    @wraps(func)
    def func_wrapper(*args, **kwargs):
        '''
        Append id to return
        :param args:
        :param kwargs:
        :return: function
        '''
        re = func(*args, **kwargs)
        re.update({'id': _id})
        return re
    return func_wrapper


class BaseService(object):
    def __init__(self, service_name):
        self.handler = {}
        self.handler_keys = []
        self.service_name = service_name

    def add_handler(self, func):
        assert callable(func)
        key = BaseService.get_id(func)
        self.handler_keys.append(key)
        self.handler[key] = func

    def del_handler(self, key): pass

    def __getitem__(self, key):
        return self.get_handler(key)

    def get_handler(self, key):
        assert isinstance(key, (unicode, str)) is True
        try:
            return self.handler[key]
        except KeyError:
            print_trace_exception()
            raise ServiceHandlerMissingException()

    def get_handler_list(self):
        return self.handler.keys()

    def get_handler_id(self, key):
        self.get_handler(key)
        return '{}_{}'.format(self.service_name, key)

    def get_name(self):
        return self.service_name

    @classmethod
    def get_id(cls, func):
        return str(func.__name__).upper()
