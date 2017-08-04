from functools import wraps


class ServiceException(Exception):
    pass


class ServiceHandlerMissingException(ServiceException):
    pass


def Handler(func):
    _id = BaseService.get_id(func)

    @wraps(func)
    def func_wrapper(*args, **kwargs):
        '''
        Append id to return
        :param args:
        :param kwargs:
        :return: function
        '''
        return func(*args, **kwargs).update({'id': _id})
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

    def get_handler(self, key):
        assert isinstance(key, (unicode, str)) is True
        try:
            return self.handler[key]
        except KeyError:
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
        return str(func.__name__).capitalize()
