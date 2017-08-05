import logging
from baseservice import BaseService, handler


class ChatService(BaseService):

    def __init__(self):
        BaseService.__init__(self, 'ChatService')
        self.chat_room_list = [0]
        self.lobby_chat_room_id = 0
        self.chat_room = {0: {}}
        self.chat_root_content = {0: []}

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
        def send_msg(uid, cid, msg):
            if cid not in self.chat_root_content:
                return {'code': 404, 'msg': 'cannot send msg. Room not exists or User not in the room'}
            if uid not in self.chat_room[cid]:
                return {'code': 404, 'msg': 'cannot send msg. Room not exists or User not in the room'}
            return self.chat_root_content[cid]
        self.add_handler(send_msg)