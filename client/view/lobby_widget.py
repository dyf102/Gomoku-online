#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
from login_widget import LoginDialog
from time import sleep

sys.path.append('../')
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
        self.login = LoginDialog(self)
        self.login.open()
        #signal
        self.connect(self.login_controller, SIGNAL("login_callback"),
                    self.login_callback)
        self.connect(self.login, SIGNAL("close"),
                     self.close_login_dialog)



    def close_login_dialog(self):
        if self.login_controller.is_login():
            self.login.close()

    def login_callback(self, code, username):
        msg = QMessageBox(self)
        if code == 200:
            msg.setIcon(QMessageBox.Information)
            msg.setText("Login Successfully: Welcome {}".format(username))
        else:
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Login Failed: code {}".format(code))
        msg.show()
        sleep(2)
        msg.close()


class GameLobbyFrame(QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.parent = parent
