# -*- encoding:utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from chat_widget import ChatWidget
from chessboard_widget import ChessBoard
from game_control import GameControlWidget


class GameWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.resize(800, 520)
        self.chat = ChatWidget(self)

        self.chessboard = ChessBoard(self)
        self.game_control = GameControlWidget(self)
        self.game_control.setGeometry(520, 370, 270, 130)
        self.isClosable = False

    def closeEvent(self, event):
        if not self.isClosable:
            ret = QMessageBox(self).information(None, 'Warning',
                                                'Quit will lead to the end of game\n'
                                                'Do you make sure to quit the game?',
                                                'Yes', 'No')
            if ret == 0:
                self.isClosable = True
                self.close()
                #game_room_manager.GameRoomManager().leaveRoom()
            else:
                event.ignore()