#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import QListView, \
    QMessageBox, QListWidgetItem, QStandardItemModel, QFont,\
    QAbstractItemView, QStandardItem
from PyQt4.QtCore import QString, SIGNAL, QSize, Qt, pyqtSlot
from controller.game_controller import GameController
import logging


class GameListWidget(QListView):

    def __init__(self, parent=None):
        QListView.__init__(self, parent)
        self.game_list = []
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.setWordWrap(True)
        self.setUniformItemSizes(True)
        self.setGridSize(QSize(self.rect().width(), 30))
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAcceptDrops(True)
        self.game_controller = GameController()
        self.game_controller.connector.connect(SIGNAL('game_list'), self.add_game_item)

    #@pyqtSlot(unicode)
    def add_game_item(self, txt):
        print"--------------------------------"
        item = QStandardItem(txt)
        item.setTextAlignment(Qt.AlignCenter)
        self.model.appendRow(item)
