#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import QListView, \
    QMessageBox, QListWidgetItem, QStandardItemModel, QFont,\
    QAbstractItemView, QStandardItem
from PyQt4.QtCore import QString, SIGNAL, QSize, Qt
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
        self.connect(self.game_controller, SIGNAL('add_item(QString)'), self.add_item)

    def Clicked(self, item):
        QMessageBox.information(self, "ListWidget", "You clicked: " + item.text())

    def add_item(self, txt):
        logging.debug("Add %s", txt)
        item = QStandardItem(txt)
        item.setTextAlignment(Qt.AlignCenter)
        self.model.appendRow(item)
