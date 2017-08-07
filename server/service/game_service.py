import logging
import time

from baseservice import BaseService, handler, register

from model.game import Game
LOBBY_CHAT_ID = 0


class GameService(BaseService):

    def __init__(self):
        BaseService.__init__(self, 'ChatService')
        self.game_list = []
        self.game_list.append(Game(123, 'AAA', 234, 'BBB'))

    def load_handlers(self):
        @register(self)
        @handler
        def get_game_list(self):
            return {'code': 200, 'list': self.game_list}
