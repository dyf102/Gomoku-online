
# !/usr/bin/env python
# -*- coding: utf-8 -*-

# import sys
import logging
# import json as JSON
# import redis
from baseservice import BaseService, handler
from model.user import User


class UserService(BaseService):

    def __init__(self):
        BaseService.__init__(self, 'UserService')
        self.current_user = {}
        self.load_handlers()

    def load_handlers(self):
        # self.add_is_idle()
        self.add_login()
        self.add_logout()
        self.add_get_idle_user()
        self.add_get_rank()
    # def add_is_idle(self):
    #    @handler
    #    def is_idle(client_id):
    #        return {'code': 200, 'status':
    #                self.current_user.get(client_id)}
    #    self.add_handler(is_idle)

    def add_login(self):
        @handler
        def login(client_id, user_info):
            username, uid, = user_info['username'], client_id
            self.current_user[client_id] = User(username=username, uid=uid)
            return {'code': 200, 'uid': client_id, 'username': user_info['username']}

        self.add_handler(login)

    def add_logout(self):
        @handler
        def logout(client_id):
            self.current_user[client_id] = None
            return {'code': 200, 'uid': client_id}

        self.add_handler(logout)

    def add_get_idle_user(self):
        @handler
        def get_idle_list(client_id):
            return {'code': 200, 'idle_list': self.current_idle_user}
        self.add_handler(get_idle_list)

    def add_get_rank(self):
        @handler
        def get_user_rank(client_id):
            return {'code': 200, 'list': sorted(self.current_user, key=lambda user: user.point)}

        self.add_handler(get_user_rank)

