#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtGui import QtGui, QtCore

import sys


class ChessboardWidget(QtGui.QWidget):
   def __init__(self):
   	super(ChessboardWidget, self).__init__()
    palette = QPalette()
    palette.setBrush(QPalette.Background, QBrush(
        QPixmap("./images/chessboard.png")))

    window.setPalette(palette)
    window.setWindowTitle("QMainWindow Background Image")
    window.show()

    return app.exec_()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()