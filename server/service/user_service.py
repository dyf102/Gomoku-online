
# !/usr/bin/env python
# -*- coding: utf-8 -*-

# import sys
import logging
# import json as JSON
# import redis
from baseservice import BaseService, handler


class UserService(BaseService):

    def __init__(self):
        BaseService.__init__(self, 'UserService')
        self.current_user = {}
        self.current_idle_user = {}
        self.load_handlers()

    def load_handlers(self):
        self.add_is_idle()
        self.add_login()
        self.add_logout()
        self.add_get_idle_user()

    def add_is_idle(self):
        @handler
        def is_idle(client_id):
            return {'code': 200, 'status':
                    client_id in self.current_idle_user.keys()}
        self.add_handler(is_idle)

    def add_login(self):
        @handler
        def login(client_id, user_info):
            self.current_user[client_id] = user_info
            self.current_idle_user[client_id] = user_info
            return {'code': 200, 'uid': client_id, 'uinfo': user_info}

        self.add_handler(login)

    def add_logout(self):
        @handler
        def logout(client_id):
            self.current_user[client_id] = None
            self.current_idle_user[client_id] = None
            return {'code': 200, 'uid': client_id}

        self.add_handler(logout)

    def add_get_idle_user(self):
        @handler
        def get_idle_list(client_id):
            return {'code': 200, 'idle_list': self.current_idle_user}
        self.add_handler(get_idle_list)
