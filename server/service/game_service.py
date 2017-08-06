import logging
import time

from baseservice import BaseService, handler

LOBBY_CHAT_ID = 0


class GameService(BaseService):

    def __init__(self):
        BaseService.__init__(self, 'ChatService')
