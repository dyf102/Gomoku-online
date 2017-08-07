
# !/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from baseservice import BaseService, handler, register
from model.user import User


class UserService(BaseService):

    def __init__(self):
        BaseService.__init__(self, 'UserService')
        self.current_user = {}
        self.load_handlers()

    def load_handlers(self):
        # self.add_is_idle()
        # self.add_login()
        # self.add_logout()
        # self.add_get_idle_user()
        # self.add_get_rank()

        @register(self)
        @handler
        def login(uid, username):
            self.current_user[uid] = User(username=username, uid=uid)
            return {'code': 200, 'uid': uid, 'username': username}

        @register(self)
        @handler
        def logout(uid):
            self.current_user[uid] = None
            return {'code': 200, 'uid': uid}

        @register(self)
        @handler
        def get_idle_list(uid):
            return {'code': 200, 'idle_list': self.current_idle_user}

        @register(self)
        @handler
        def get_user_rank(uid):
            rank_list = []
            # TODO: to add max-heap to store current user
            # TODO: cache the result
            for _, user in self.current_user.items():
                rank_list.append(user)
            user_list = map(lambda u: u.__dict__, sorted(rank_list, key=lambda x: x.point))
            return {'code': 200, 'list': user_list}

