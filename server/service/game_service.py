import logging
import time

from baseservice import BaseService, handler, register

from model.game import Game, STATUS_EMPTY, STATUS_WAITING, STATUS_FIGHTING
LOBBY_CHAT_ID = 0


class GameService(BaseService):

    def __init__(self):
        BaseService.__init__(self, 'GameService')
        # self.game_list = []
        self.game_dict = {}
        self.load_handlers()
        self.add_new_game(123, 'AAA', 234, 'BBB')

    def add_new_game(self, user1, user1_id, user2=None, user2_id=None):
        g = Game(user1, user1_id, user2, user2_id)
        # self.game_list.append(g)
        self.game_dict[g.get_id()] = g
        return g

    def load_handlers(self):
        @register(self)
        @handler
        def get_game_list(uid):
            return {'code': 200, 'list': [x for _, x in self.game_dict.items()]}

        @register(self)
        @handler
        def create_new_game(uid, username):
            g = self.add_new_game(uid, username)
            return {'code': 200, 'gid': g.get_id()}

        @register(self)
        @handler
        def enter_game(uid, username, gid):
            try:
                g = self.game_dict[gid]
                status = 'guest'
                if uid in (g.host_id, g.guest_id):
                    return {'code': 404, 'msg': '%d already in the game %d'.format(uid, gid)}
                if g.status not in (STATUS_EMPTY or STATUS_WAITING):
                    return {'code': 404, 'msg': 'The game %d is already started'.format(uid, gid)}
                if g.guest_id and g.host_id:
                    return {'code': 404, 'msg': 'The room is full'}
                elif g.guest_id is None:
                    g.guest_id = uid
                    g.gues_name = username
                else:  # g.host_id is None:
                    g.host_id = uid
                    g.host_name = username
                    status = 'host'
                self.game_dict[gid] = g
                return {'code': 200, 'status': status}
            except KeyError:
                return {'code': 404, 'msg': 'gid not found'}

        @register(self)
        @handler
        def exit_game(uid, gid):
            try:
                g = self.game_dict[uid]
                if not g.is_in_game(uid):
                    return {'code': 404, 'msg': '%d not in the room %s'.format(uid, gid)}
                if g.host_id == uid:
                    g.host_id = None
                    g.host_name = None
                elif g.guest_id == uid:
                    g.guest_id = None
                    g.guest_name = None
                if g.status == STATUS_FIGHTING:
                    g.status = STATUS_WAITING
                    self.game_dict[uid] = g
                else:  # g.status == STATUS_WAITING: or empty
                    self.game_dict.pop(uid)  # delete the game from the dict
            except KeyError:
                return {'code': 404, 'msg': 'gid not found'}
