#!/usr/bin/env python
# -*- coding: utf-8 -*-

from service.user_service import UserService
from service.chat_service import ChatService
from application import Application

from util.util import print_trace_exception
# sys.path.append('../')



def main():
    game = Application([UserService, ChatService])
    game.run()

if __name__ == '__main__':
    main()
