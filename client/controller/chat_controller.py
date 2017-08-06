
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
import os
# import json as JSON
from network import Client
from PyQt4.QtCore import SIGNAL, QObject, QString
from basecontroller import BaseController, singleton
sys.path.append('../')
from util.util import print_trace_exception, log_callback


SEND_MSG_ID = 'SEND_MSG'
GET_MSG_ID = 'GET_MSG'
JOIN_CHAT_ROOM_ID = 'JOIN_CHAT_ROOM'
SERVICE_NAME = 'ChatService'


@singleton
class ChatController(BaseController):

    def __init__(self):
        BaseController.__init__(self, SERVICE_NAME)

    def send_msg(self, cid, uid, msg, username):
        client = self.get_client()
        req = {
            'cid': cid,
            'uid': uid,
            'msg': msg,
            'username': username
        }
        client.register(SEND_MSG_ID, self.send_msg_cb)
        client.send(service_name=SERVICE_NAME, method=SEND_MSG_ID, msg=req)

    def add_polling_msg_task(self, cid, uid):
        client = self.get_client()
        client.set_periodic_task(self.get_msg, (cid, uid), self.get_msg_cb)

    @log_callback
    def send_msg_cb(self, data):
        logging.debug('send_msg %s', data)
        self.emit(SIGNAL("send_msg_callback(int)"), data['code'])

    def get_msg(self, cid, uid):
        logging.debug('Call get msg %d %d', cid, uid)
        client = self.get_client()
        req = {
            'cid': cid,
            'uid': uid
        }
        client.register(GET_MSG_ID, self.get_msg_cb)
        client.send(service_name=SERVICE_NAME, method=GET_MSG_ID, msg=req)

    @log_callback
    def get_msg_cb(self, data):
        logging.debug('send_msg %s', data)

    def join_chat_room(self, cid, uid):
        client = self.get_client()
        req = {
            'cid': cid,
            'uid': uid,
        }
        client.register(JOIN_CHAT_ROOM_ID, self.join_chat_room_cb)
        client.send(service_name=SERVICE_NAME, method=JOIN_CHAT_ROOM_ID, msg=req)

    @log_callback
    def join_chat_room_cb(self, data):
        code = data.get('code')
        if code == 200:
            cid = data.get('cid')
            uid = data.get('uid')
            self.add_polling_msg_task(cid=cid, uid=uid)
        else:
            self.emit(SIGNAL("error_msg(QString)"), QString(data['code']))
