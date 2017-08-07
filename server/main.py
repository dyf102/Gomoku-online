#!/usr/bin/env python
# -*- coding: utf-8 -*-

from service.user_service import UserService
from service.chat_service import ChatService
from service.game_service import GameService

from application import Application
import sys
import logging


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] '
                               '- %(levelname)s: %(message)s',
                        filename='server.log')
    game = Application([UserService, ChatService, GameService])
    game.run()

if __name__ == '__main__':
    main()
