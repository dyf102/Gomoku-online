#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
from login_widget import LoginDialog
from chat_widget import ChatWidget
from rank_widget import RankList
from gamelist_widget import GameListWidget
from game_window_widget import GameWindow
import logging

# sys.path.append('../')
from controller.user_controller import UserController
from controller.chat_controller import ChatController
from controller.game_controller import GameController
from controller.basecontroller import BaseController

LOBBY_ROOM_ID = 0


class GameLobby(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.idle_list = []
        # self.resize(800, 600)
        self.setWindowFlags(Qt.Window)
        self.main_frame = GameLobbyFrame(self)
        self.main_frame.setGeometry(0, 0, 800, 600)
        # Controller
        self.user_controller = UserController()
        self.chat_controller = ChatController()
        # UI
        self.login_widget = LoginDialog(self)

        if not self.user_controller.is_login():
            self.login_widget.open()
        # signal
        self.connect(self.user_controller, SIGNAL("login_callback(int,QString)"), self.login_callback)

        self.connect(self.login_widget, SIGNAL("close"),
                     self.close_login_dialog)
        self.connect(self.login_widget, SIGNAL("login(QString,int,QString)"),
                     self.login)
        self.connect(self.chat_controller, SIGNAL("error_msg(QString)"), self.error_msg)
        self.msg_box = QMessageBox()

    def close_login_dialog(self):
        if self.user_controller.is_login():
            self.login_widget.canClose = True
            self.login_widget.close()

    def login_callback(self, code, username):
        logging.debug('widget login callback%d %s', code, username)
        if code == 200:
            self.msg_box.setIcon(QMessageBox.Information)
            self.msg_box.setText("Login Successfully: Welcome {}".format(username))
            logging.debug("Login Successfully: Welcome {}".format(username))
            # try to join the lobby chat room
            uid = self.user_controller.current_user_id
            self.chat_controller.join_chat_room(cid=LOBBY_ROOM_ID, uid=uid)
        else:
            self.msg_box.setIcon(QMessageBox.Warning)
            self.msg_box.setText("Login Failed: code {}".format(code))
        ret = self.msg_box.exec_()
        if ret == 1024:
            self.close_login_dialog()
        self.msg_box.close()

    def login(self, addr, port, username):
        if isinstance(username, QString):
            username = unicode(username)
        if isinstance(addr, QString):
            addr = unicode(addr)
        if not (self.user_controller.is_connecting or
                self.user_controller.is_connected):
            self.user_controller.connect_client(addr, port)
            self.user_controller.login(username)
        else:
            self.msg_box.setIcon(QMessageBox.Warning)
            self.msg_box.setText("Network is busy")
            self.msg_box.exec_()

    def error_msg(self, msg):
        self.msg_box.setText(msg)
        self.msg_box.exec_()


class GameLobbyFrame(QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.rid = LOBBY_ROOM_ID
        self.parent = parent
        self.setGeometry(0, 0, 800, 600)

        self.game_controller = GameController()
        # UI
        self.game_list_widget = GameListWidget(self)
        # self.game_windows = GameWindow(self, rid=1)

        self.game_list_widget.setGeometry(40, 40, 550, 450)
        # self.game_list_widget.connect(BaseController(service_name='game_controller'),
        #                              SIGNAL('add_game_item(QString)'),
        #                              self.game_list_widget.add_game_item,
        #                              Qt.DirectConnection)

        self.rankTitle = QLabel(self)
        self.rankTitle.setText('Rank')
        self.rankTitle.setStyleSheet(QString(u"font: 75 14pt \"微软雅黑\";\n \
                                               color: rgb(100, 100, 200);"))
        self.rankTitle.setAlignment(Qt.AlignCenter)
        self.rankTitle.setGeometry(600, 20, 190, 20)
        self.rankList = RankList(self)
        self.rankList.setGeometry(600, 55, 190, 180)

        self.lobbyChat = ChatWidget(self)
        self.lobbyChat.input_box.setGeometry(600, 480, 190, 30)
        self.lobbyChat.chat_view.setGeometry(600, 250, 190, 220)

        self.lobbyChat.chat_view.connect(ChatController(),
                                         SIGNAL('showRoomTextWithRGB(QString,int,int,int)'),
                                         self.lobbyChat.chat_view.showText)
        self.lobbyChat.chat_view.connect(ChatController(),
                                         SIGNAL('clear'),
                                         self.lobbyChat.chat_view.clear)
        self.lobbyChat.chat_view.connect(GameController(),
                                         SIGNAL('showRoomTextWithRGB(QString,int,int,int)'),
                                         self.lobbyChat.chat_view.showText)




