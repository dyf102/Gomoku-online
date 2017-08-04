
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import json as JSON
import redis



class UserService(object):

    def __init__(self):
        self.current_user = {}
        self.current_idle_user = {}
        self.add_login_signout()
        self.handler
    def add_login_signout(self):
        _id = 'LOGIN'

        def login(client_id, user_info):
            self.current_user[client_id] = user_info
            self.current_idle_user[client_id] = user_info
            return {'id': _id, 'code': 200, 'uid': client_id, 'uinfo': user_info}

        def signout(client_id):
            self.current_user[client_id] = None
            self.current_idle_user[client_id] = None

        self.server.set_handler(_id, login)
        self.server.set_at_exit(signout)

    def add_get_idle_user(self):
        def get_idle_list(_):
            return self.current_idle_user

        self.server.set_handler('get_idle_list', get_idle_list)