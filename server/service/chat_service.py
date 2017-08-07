import logging
import time

from baseservice import BaseService, handler, register

LOBBY_CHAT_ID = 0


class ChatService(BaseService):

    # TODO: Add FIFO policy to the dict to limit the msg in memory

    def __init__(self):
        BaseService.__init__(self, 'ChatService')
        # init
        self.chat_room_list = []
        self.chat_room = {}
        self.chat_root_content = {}
        # next cid
        self.next_cid = LOBBY_CHAT_ID
        # init lobby
        self.make_new_chat_room()
        self.load_handlers()

    def make_new_chat_room(self, uid=None):
        cid = self.next_cid
        self.next_cid += 1
        self.chat_room_list.append(cid)
        self.chat_room[cid] = [] if uid is None else [uid]
        self.chat_root_content[cid] = []

    def load_handlers(self):
        @register(self)
        @handler
        def join_chat_room(uid, cid):
            if cid in self.chat_room_list:
                self.chat_room[cid].append(uid)
                return {'code': 200, 'uid': uid, 'cid': cid}
            else:
                return {'code': 404}
        self.add_handler(join_chat_room)

        @register(self)
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

        @register(self)
        @handler
        def get_msg(cid, uid):
            if cid not in self.chat_root_content:
                return {'code': 404, 'msg': 'cannot send msg. Room not exists or User not in the room'}
            if uid not in self.chat_room[cid]:
                return {'code': 404, 'msg': 'uid %d not in the room cid: %d'.format(uid, cid)}
            content_list = self.chat_root_content[cid]
            # size = min(len(content_list), 20)  # avoid size exceed
            msgs = content_list  # self.chat_root_content[cid][-size:]
            return {'code': 200, 'cid': cid, 'data': msgs, 'token': str(hash(str(msgs)))}

        @register(self)
        @handler
        def get_room_msg_list_hash(cid):
            if cid not in self.chat_root_content:
                return {'code': 404, 'msg': 'cannot send msg. Room not exists or User not in the room'}
            return {'code': 200, 'token': hash(str(self.chat_root_content[cid]))}
