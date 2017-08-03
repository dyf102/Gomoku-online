#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *


class GameListWidget(QListView):
    def __init__(self, parent):
        QListView.__init__(self, parent)
        self.game_list = []