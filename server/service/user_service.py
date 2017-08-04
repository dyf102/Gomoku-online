
# !/usr/bin/env python
# -*- coding: utf-8 -*-

# import sys
import logging
# import json as JSON
# import redis
from baseservice import BaseService, Handler


class UserService(BaseService):

    def __init__(self):
        BaseService.__init__(self, 'UserService')
        self.current_user = {}
        self.current_idle_user = {}
        self.add_login_signout()

    def add_is_idle(self):
        @Handler
        def is_idle(client_id):
            return {'code': 200, 'status':
                    client_id in self.current_idle_user.keys()}
        self.add_handler(is_idle)

    def add_login(self):
        @Handler
        def login(client_id, user_info):
            self.current_user[client_id] = user_info
            self.current_idle_user[client_id] = user_info
            return {'code': 200, 'uid': client_id, 'uinfo': user_info}

        self.add_handler(login)

    def add_logout(self):
        @Handler
        def logout(client_id):
            self.current_user[client_id] = None
            self.current_idle_user[client_id] = None
            return {'code': 200, 'uid': client_id}

        self.add_handler(logout)

    def add_get_idle_user(self):
        @Handler
        def get_idle_list(_):
            return {'code': 200, 'idle_list': self.current_idle_user}
        self.server.set_handler('get_idle_list', get_idle_list)
