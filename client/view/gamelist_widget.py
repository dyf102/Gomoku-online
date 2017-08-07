#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import QListWidget, QMessageBox
from PyQt4.QtCore import *
from controller.chat_controller import ChatController


class GameListWidget(QListWidget):
    def __init__(self, parent=None):
        QListWidget.__init__(self, parent)
        self.game_list = []
        # for i in range(10):
        #    self.addItem(str(i))
        self.itemClicked.connect(self.Clicked)
        self.connect(ChatController(), SIGNAL('addItem(QString)'), self.addItem)

    def Clicked(self, item):
        QMessageBox.information(self, "ListWidget", "You clicked: " + item.text())

