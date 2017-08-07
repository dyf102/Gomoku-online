#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import QListWidget, QMessageBox
from PyQt4.QtCore import *


class GameListWidget(QListWidget):
    def __init__(self, parent=None):
        QListWidget.__init__(self, parent)
        self.game_list = []
        for i in range(10):
            self.addItem(str(i))
        self.itemClicked.connect(self.Clicked)

    def Clicked(self, item):
        QMessageBox.information(self, "ListWidget", "You clicked: " + item.text())
