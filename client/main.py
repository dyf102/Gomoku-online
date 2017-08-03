# -*- encoding: UTF-8 -*-

import logging
import sys
from PyQt4 import QtGui

from view.login_widget import LoginDialog
from view.chat_widget import ChatView
from view.chessboard_widget import ChessBoard
from view.game_window_widget import GameWindow

sys.path.append('../')
sys.path.append('./res')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] '
                               '- %(levelname)s: %(message)s',
                        filename='example.log')
    app = QtGui.QApplication(sys.argv)
    window = GameWindow()
    window.setWindowTitle(u"五子棋")
    window.show()
    sys.exit(app.exec_())
