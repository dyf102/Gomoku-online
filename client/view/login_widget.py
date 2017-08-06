# -*- encoding: UTF-8 -*-
# !/usr/bin/env python
from PyQt4.QtCore import *
from PyQt4.QtGui import QApplication, QIcon, \
    QDialog, QLabel, QLineEdit, QPushButton
import sys


DEFAULT_PORT = 8888
DEFAULT_ADDR = '127.0.0.1'

WINDOW_WIDTH = 450
WINDOW_HEIGHT = 350


class LoginDialog(QDialog):
    def __init__(self, parent=None, title='User Login'):
        QDialog.__init__(self, parent)
        window_size = QApplication.desktop().size()
        self.setStyleSheet("background-color: white")
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.canClose = False
        self.setWindowTitle(title)
        self.setMaximumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowIcon(QIcon(':white'))
        self.setGeometry((window_size.width() - WINDOW_WIDTH) / 2,
                         (window_size.height() - WINDOW_HEIGHT) / 2 + 50,
                         WINDOW_WIDTH, WINDOW_HEIGHT)

        ipLbl = QLabel(self)
        ipLbl.setAlignment(Qt.AlignRight)
        ipLbl.setGeometry(70, 80, 60, 20)
        ipLbl.setText('Server IP')

        portLbl = QLabel(self)
        portLbl.setAlignment(Qt.AlignRight)
        portLbl.setGeometry(70, 120, 60, 20)
        portLbl.setText('Port')

        userLbl = QLabel(self)
        userLbl.setAlignment(Qt.AlignRight)
        userLbl.setGeometry(60, 160, 70, 20)
        userLbl.setText('Username')

        self.ipEdit = QLineEdit(self)
        self.ipEdit.setPlaceholderText(DEFAULT_ADDR)
        self.ipEdit.setFocusPolicy(Qt.ClickFocus)
        self.ipEdit.setGeometry(160, 80, 130, 20)

        self.portEdit = QLineEdit(self)
        self.portEdit.setPlaceholderText(str(DEFAULT_PORT))
        self.portEdit.setFocusPolicy(Qt.ClickFocus)
        self.portEdit.setGeometry(160, 120, 130, 20)

        self.userEdit = QLineEdit(self)
        self.userEdit.setGeometry(160, 160, 130, 20)

        loginBtn = QPushButton(self)
        loginBtn.setText('Login')
        loginBtn.clicked.connect(self.login_event)
        loginBtn.setGeometry(210, 220, 85, 30)

        quitBtn = QPushButton(self)
        quitBtn.setText('Quit')
        quitBtn.clicked.connect(parent.close)
        quitBtn.setGeometry(90, 220, 85, 30)

    def login_event(self):
        if not self.userEdit.text().length():
            return
        self.emit(SIGNAL("login(QString,int,QString)"),
                  self.ipEdit.text() if self.ipEdit.text().length() else DEFAULT_ADDR,
                  self.portEdit.text().toLong() if self.portEdit.text().length() else DEFAULT_PORT,
                  self.userEdit.text())

    def closeEvent(self, event):
        if not self.canClose:
            self.emit(SIGNAL("close"))
            event.ignore()
