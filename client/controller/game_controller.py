#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
import json as JSON
from network import Client
from PyQt4.QtCore import SIGNAL, QObject
from basecontroller import BaseController

SERVICE_NAME = 'GameService'


class GameController(BaseController):

    def __init__(self):
        BaseController.__init__(self, service_name=SERVICE_NAME)

