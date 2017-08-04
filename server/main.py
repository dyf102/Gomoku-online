#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import json as JSON
import redis
from server import Server

sys.path.append('../')



class Application(object):

    def __init__(self):
        self.server = Server()




    def run(self):
        self.server.bind()
        try:
            self.server.listen()
        except KeyboardInterrupt as k:
            self.server.stop()
            raise k

def main():
    game = Application()
    game.run()

if __name__ == '__main__':
    main()
