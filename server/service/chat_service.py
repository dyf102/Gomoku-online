import logging
import time

from baseservice import BaseService, handler


class ChatService(BaseService):

    ## TODO: Add FIFO fix size dict to limit the msg in memory

    def __init__(self):
        BaseService.__init__(self, 'ChatService')
        self.chat_room_list = [0]
        self.lobby_chat_room_id = 0
        self.chat_room = {0: []}
        self.chat_root_content = {0: []}

    def load_handlers(self):
        self.add_join_chat_room()
        self.add_send_msg()
        self.add_get_msg()

    def add_join_chat_room(self):
        @handler
        def join_chat_room(uid, cid):
            if cid in self.chat_room_list:
                self.chat_room[uid].append(cid)
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
            return self.chat_root_content[cid].append(
                {'time': time.strftime("%Y-%m-%d %H:%M"), 'username': username, 'msg': msg})
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