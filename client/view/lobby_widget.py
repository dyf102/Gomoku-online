#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
from login_widget import LoginDialog
sys.path.append('../controller')
from user_controller import UserController


class GameLobby(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.idle_list = []
        self.resize(800, 600)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint |
                            Qt.WindowMinMaxButtonsHint)
    	self.login_controller = UserController

    	#signal
    	self.connect(self.login_controller, SIGNAL("loginCallback(int)"),
	                     self.loginCallback)
    	self.connect(self.loginDialog, SIGNAL("close"),
                     self.loginDialogClose)
    	# UI
    	self.login = LoginDialog(self)

    def closeLoginDialog(self):
    	if self.login_controller.is_login():
    		self.login.close()
class GameLobbyFrame(QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.parent = parent
