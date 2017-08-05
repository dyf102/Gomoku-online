
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
import os
# import json as JSON
from network import Client
from PyQt4.QtCore import SIGNAL, QObject, QString
from basecontroller import BaseController
sys.path.append('../')
from util.util import print_trace_exception

SEND_MSG_ID = 'SEND_MSG'
GET_MSG_ID = 'GET_MSG'

SERVICE_NAME = 'ChatService'


class ChatController(BaseController):

    def __init__(self):
        BaseController.__init__(self)

    def send_msg(self, cid, uid, msg):
        client = self.get_client()
        req = {
            'id': SEND_MSG_ID,
            'cid': cid,
            'uid': uid,
            'msg': msg
        }
        client.register(SEND_MSG_ID, self.login_callback)
        client.send(SERVICE_NAME, SEND_MSG_ID, req)

    def send_msg_cb(self, data):
        logging.debug('send_msg %s', data)
        self.emit(SIGNAL("send_msg_callback(int)"), data['code'])

    def get_msg(self, cid, uid):
        client = self.get_client()
        req = {
            'id': GET_MSG_ID,
            'cid': cid,
            'uid': uid
        }

    def get_msg_cb(self, data):
        logging.debug('send_msg %s', data)
