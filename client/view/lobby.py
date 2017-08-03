#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class GameLobby(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.idle_list = []
        self.resize(800, 600)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint |
                            Qt.WindowMinMaxButtonsHint)


class GameLobbyFrame(QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.parent = parent
