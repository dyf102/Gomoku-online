
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
from util.util import print_trace_exception, log_callback

SEND_MSG_ID = 'SEND_MSG'
GET_MSG_ID = 'GET_MSG'
JOIN_CHAT_ROOM_ID = 'JOIN_CHAT_ROOM'
SERVICE_NAME = 'ChatService'


class ChatController(BaseController):

    def __init__(self):
        BaseController.__init__(self, SERVICE_NAME)

    def send_msg(self, cid, uid, msg, username):
        client = self.get_client()
        req = {
            'id': SEND_MSG_ID,
            'cid': cid,
            'uid': uid,
            'msg': msg,
            'username': username
        }
        client.register(SEND_MSG_ID, self.send_msg_cb)
        client.send(SERVICE_NAME, SEND_MSG_ID, req)

    @log_callback
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

    @log_callback
    def get_msg_cb(self, data):
        logging.debug('send_msg %s', data)

    def join_chat_room(self, cid, uid):
        client = self.get_client()
        req = {
            'id': JOIN_CHAT_ROOM_ID,
            'cid': cid,
            'uid': uid,
        }
        client.register(JOIN_CHAT_ROOM_ID, self.join_chat_room_cb)
        client.send(SERVICE_NAME, JOIN_CHAT_ROOM_ID, req)

    @log_callback
    def join_chat_room_cb(self, data):
        pass
