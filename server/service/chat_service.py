import logging
import time

from baseservice import BaseService, handler

LOBBY_CHAT_ID = 0


class ChatService(BaseService):

    # TODO: Add FIFO fixed size dict to limit the msg in memory

    def __init__(self):
        BaseService.__init__(self, 'ChatService')
        # init
        self.chat_room_list = []
        self.chat_room = {}
        self.chat_root_content = {}
        # next cid
        self.next_cid = LOBBY_CHAT_ID
        self.make_new_chat_room()
        self.load_handlers()

    def load_handlers(self):
        self.add_join_chat_room()
        self.add_send_msg()
        self.add_get_msg()

    def make_new_chat_room(self, uid=None):
        cid = self.next_cid
        self.next_cid += 1
        self.chat_room_list.append(cid)
        self.chat_room[cid] = [] if uid is None else [uid]
        self.chat_root_content[cid] = []

    def add_join_chat_room(self):
        @handler
        def join_chat_room(uid, cid):
            if cid in self.chat_room_list:
                self.chat_room[cid].append(uid)
                return {'code': 200, 'content': self.chat_root_content[cid]}
            else:
                return {'code': 404}
        self.add_handler(join_chat_room)

    def add_send_msg(self):
        @handler
        def send_msg(uid, username, cid, msg):
            if cid not in self.chat_root_content:
                return {'code': 404, 'msg': 'cannot send msg. Room not exists or User not in the room'}
            if uid not in self.chat_room[cid]:
                return {'code': 404, 'msg': 'cannot send msg. Room not exists or User not in the room'}
            if len(msg) >= 100:
                return {'code': 404, 'msg': 'msg is too long(less 100 characters)'}
            self.chat_root_content[cid].append(
                {'time': time.strftime("%Y-%m-%d %H:%M"), 'username': username, 'msg': msg})
            return {'code': 200, 'msg': ''}

        self.add_handler(send_msg)

    def add_get_msg(self):
        @handler
        def get_msg(cid, size=20):
            if cid not in self.chat_root_content:
                return {'code': 404, 'msg': 'cannot send msg. Room not exists or User not in the room'}
            content_list = self.chat_root_content[cid]
            size %= len(content_list)  # avoid size exceed
            return self.chat_root_content[cid][-size:]
        self.add_handler(get_msg)
