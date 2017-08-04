#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
from login_widget import LoginDialog
from time import sleep
import logging

# sys.path.append('../')
from controller.user_controller import UserController


class GameLobby(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.idle_list = []
        self.resize(800, 600)
        self.setWindowFlags(Qt.Window)
        self.main_frame = GameLobbyFrame(self)

        self.login_controller = UserController()
        # UI
        self.login_widget = LoginDialog(self)
        if not self.login_controller.is_login():
            self.login_widget.open()
        # signal
        self.connect(self.login_controller, SIGNAL("login_callback(int,QString)"),
                     self.login_callback)

        self.connect(self.login_widget, SIGNAL("close"),
                     self.close_login_dialog)
        self.connect(self.login_widget, SIGNAL("login(QString,int,QString)"),
                     self.login)
        self.msg_box = QMessageBox()

    def close_login_dialog(self):
        if self.login_controller.is_login():
            self.login_widget.canClose = True
            self.login_widget.close()

    def login_callback(self, code, username):
        logging.debug('widget login callback%d %s', code, username)
        if code == 200:
            self.msg_box.setIcon(QMessageBox.Information)
            self.msg_box.setText("Login Successfully: Welcome {}".format(username))
            logging.debug("Login Successfully: Welcome {}".format(username))
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
        if not (self.login_controller.is_connecting or
                self.login_controller.is_connected):
            self.login_controller.connect_client(addr, port)
            self.login_controller.login(username)
        else:
            self.msg_box.setIcon(QMessageBox.Warning)
            self.msg_box.setText("Network is busy")
            self.msg_box.exec_()


class GameLobbyFrame(QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.parent = parent
