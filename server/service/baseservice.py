class ServiceException(Exception):
    pass


class ServiceHandlerMissingException(ServiceException):
    pass


class BaseService(object):
    def __init__(self, service_name):
        self.handler = {}
        self.service_name = service_name

    def add_handler(self, key, func):
        assert isinstance(key, basestring) and callable(func)
        self.handler[key] = func

    def get_handler(self, key):
        assert isinstance(key, basestring)
        try:
            return self.handler[key]
        except KeyError:
            raise ServiceHandlerMissingException()

    def get_handler_list(self):
        return self.handler.keys()

    def get_handler_id(self, key):
        self.get_handler(key)
        return '{}_{}'.format(self.service_name, key)
