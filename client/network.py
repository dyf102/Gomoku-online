#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import json as JSON
import Queue

sys.path.append('../lib')
sys.path.append('../util')
from util import new_id
from netstream import netstream, NET_STATE_ESTABLISHED, NET_STATE_STOP
PORT = 8888
HOST = '127.0.0.1'
logger = logging  # .getLogger('tcpserver')
logging.basicConfig(filename='example.log', level=logging.DEBUG)


SERVICE_ID = new_id()
LOGIN_METHOD_ID = new_id()

class Client():
	
	def __init__(self, port=PORT, host=HOST):
		# Greenlet.__init__(self)
		self.c = netstream()
		self.port = port
		self.host = host
		self.c.connect(self.host, self.port)
        self.start = False

	def reciever(self):
		self.start = True
		while self.start:
        	data = self.c.recv()
			if len(data) > 0:
				logger.debug(data)	
			if data == 'OK':
				break

	def _run(self):
		
		while True:
			
			self.c.send('login\r\n{}'.format(JSON.dumps({'nickname': nickname})))
			data = self.c.recv()
			if len(data) > 0:
				logger.debug(data)	
				if data == 'OK':
					break
		self.c.close()
	def login(self, nickname):
		self.c.connect(self.host, self.port)
		while True:
			self.c.process()
			self.c.send('login\r\n{}'.format(JSON.dumps({'nickname': nickname})))
			data = self.c.recv()
			if len(data) > 0:
				logger.debug(data)	
				if data == 'OK':
					break
		self.c.close()
if __name__ == "__main__":
	c = Client()
	c.login('Mark')